"""
Router para el módulo de Control Financiero (cuentas por cobrar).

Rutas registradas en router.py bajo:
  admissions_finance_router → prefix /admissions
  finance_router            → prefix /finance
  charges_router            → prefix /charges
  payments_router           → prefix /payments
"""

import os
import re
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.core.deps import RoleRequired, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.finance import (
    AccountOut,
    ChargeCreate,
    ChargeOut,
    FinanceOverviewOut,
    OverdueEntryOut,
    PaymentAgreementOut,
    PaymentAgreementUpsert,
    PaymentCreate,
    PaymentOut,
)
from app.services.finance_service import FinanceService

# ──────────────────────────────────────────────────────────────────────────────
# PDF helpers
# ──────────────────────────────────────────────────────────────────────────────

AGREEMENT_LABELS = {
    "monthly": "Mensualidad",
    "fixed_total": "Monto fijo total",
    "scholarship_full": "Beca total",
    "scholarship_partial": "Beca parcial",
}

METHOD_LABELS = {
    "cash": "Efectivo",
    "sinpe": "SINPE Móvil",
    "transfer": "Transferencia",
    "check": "Cheque",
    "other": "Otro",
}

PAYER_LABELS = {
    "family": "Familia / Responsable",
    "iafa": "IAFA",
    "imas": "IMAS",
    "church": "Iglesia",
    "donor": "Donante",
    "other": "Otro",
}


def _fmt_crc(value) -> str:
    val = float(value) if not isinstance(value, (int, float)) else value
    formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"₡{formatted}"


def _jinja_env() -> Environment:
    templates_path = Path(__file__).parent.parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_path)), autoescape=True)
    env.filters["crc"] = _fmt_crc
    env.filters["method_label"] = lambda v: METHOD_LABELS.get(v, v)
    env.filters["payer_label"] = lambda v: PAYER_LABELS.get(v, v)
    env.filters["agreement_label"] = lambda v: AGREEMENT_LABELS.get(v, v)
    return env


def _render_pdf(html: str, bg: BackgroundTasks, filename: str) -> FileResponse:
    options = {
        "page-size": "A4",
        "margin-top": "0mm",
        "margin-right": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "encoding": "UTF-8",
        "no-outline": None,
        "enable-local-file-access": None,
    }
    import pdfkit
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        pdfkit.from_string(html, tmp_path, options=options)
    except Exception as exc:
        os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {exc}") from exc
    bg.add_task(os.unlink, tmp_path)
    return FileResponse(path=tmp_path, media_type="application/pdf", filename=filename)

_finance_required = RoleRequired(["admin", "receptionist"])

# ──────────────────────────────────────────────────────────────────────────────
# /admissions/{id}/…
# ──────────────────────────────────────────────────────────────────────────────
admissions_finance_router = APIRouter()


@admissions_finance_router.get("/{admission_id}/payment-agreement", response_model=PaymentAgreementOut)
def get_payment_agreement(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    agreement = FinanceService(db).get_agreement(admission_id)
    if not agreement:
        raise HTTPException(status_code=404, detail="Acuerdo de pago no encontrado")
    return agreement


@admissions_finance_router.put(
    "/{admission_id}/payment-agreement",
    response_model=PaymentAgreementOut,
    status_code=200,
)
def upsert_payment_agreement(
    admission_id: int,
    data: PaymentAgreementUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    return FinanceService(db).upsert_agreement(admission_id, data)


@admissions_finance_router.get("/{admission_id}/charges", response_model=List[ChargeOut])
def list_charges(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    return FinanceService(db).list_charges(admission_id)


@admissions_finance_router.post(
    "/{admission_id}/charges",
    response_model=ChargeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_charge(
    admission_id: int,
    data: ChargeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_finance_required),
):
    return FinanceService(db).create_charge(admission_id, data, current_user.id)


@admissions_finance_router.get("/{admission_id}/payments", response_model=List[PaymentOut])
def list_payments(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    return FinanceService(db).list_payments(admission_id)


@admissions_finance_router.post(
    "/{admission_id}/payments",
    response_model=PaymentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    admission_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    return FinanceService(db).create_payment(admission_id, data)


@admissions_finance_router.get("/{admission_id}/account", response_model=AccountOut)
def get_account(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    return FinanceService(db).get_account(admission_id)


@admissions_finance_router.get("/{admission_id}/account/statement")
def get_account_statement(
    admission_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    ctx = FinanceService(db).get_statement_context(admission_id)
    ctx["generated_at"] = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    ctx["agreement_labels"] = AGREEMENT_LABELS
    env = _jinja_env()
    html = env.get_template("finance_statement.html").render(**ctx)
    adm_num = ctx["admission"].admission_number
    return _render_pdf(html, bg, filename=f"estado_cuenta_{adm_num}.pdf")


# ──────────────────────────────────────────────────────────────────────────────
# /charges/{id}
# ──────────────────────────────────────────────────────────────────────────────
charges_router = APIRouter()


@charges_router.delete("/{charge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_charge(
    charge_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    FinanceService(db).delete_charge(charge_id)


# ──────────────────────────────────────────────────────────────────────────────
# /payments/{id}
# ──────────────────────────────────────────────────────────────────────────────
payments_router = APIRouter()


@payments_router.get("/{payment_id}/receipt")
def get_payment_receipt(
    payment_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    payment = FinanceService(db).get_payment_for_receipt(payment_id)
    ctx = {
        "payment": payment,
        "admission": payment.admission,
        "resident": payment.admission.resident,
        "received_by": payment.received_by,
        "generated_at": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
    }
    env = _jinja_env()
    html = env.get_template("finance_receipt.html").render(**ctx)
    return _render_pdf(html, bg, filename=f"recibo_{payment.receipt_number:05d}.pdf")


# ──────────────────────────────────────────────────────────────────────────────
# /finance/…
# ──────────────────────────────────────────────────────────────────────────────
finance_router = APIRouter()

_PERIOD_RE = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])$")


def _validate_period(period: str) -> str:
    if not _PERIOD_RE.match(period):
        raise HTTPException(status_code=422, detail="El periodo debe tener el formato YYYY-MM")
    return period


@finance_router.post(
    "/generate-monthly-charges",
    response_model=List[ChargeOut],
    status_code=status.HTTP_201_CREATED,
)
def generate_monthly_charges(
    period: str = Query(..., description="Periodo en formato YYYY-MM"),
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    _validate_period(period)
    return FinanceService(db).generate_monthly_charges(period)


@finance_router.get("/overview", response_model=FinanceOverviewOut)
def get_overview(
    period: str = Query(..., description="Periodo en formato YYYY-MM"),
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    _validate_period(period)
    return FinanceService(db).get_overview(period)


@finance_router.get("/overdue", response_model=List[OverdueEntryOut])
def get_overdue(
    margin_days: int = Query(30, ge=1),
    db: Session = Depends(get_db),
    _: User = Depends(_finance_required),
):
    return FinanceService(db).get_overdue(margin_days)
