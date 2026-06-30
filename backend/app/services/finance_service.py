import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.admission import Admission, AdmissionStatus
from app.models.finance import (
    AgreementType,
    Charge,
    Payment,
    PaymentAgreement,
)
from app.models.resident import Resident
from app.models.user import User
from app.schemas.finance import (
    AccountOut,
    ChargeCreate,
    ChargeOut,
    FinanceOverviewOut,
    OverdueEntryOut,
    PaymentAgreementUpsert,
    PaymentCreate,
    PaymentOut,
)

ACTIVE_STATUSES = [
    AdmissionStatus.consents_pending,
    AdmissionStatus.assessment_in_progress,
    AdmissionStatus.treatment_active,
]

MONTH_NAMES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


class FinanceService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Agreement
    # ------------------------------------------------------------------ #

    def get_agreement(self, admission_id: int) -> Optional[PaymentAgreement]:
        return (
            self.db.query(PaymentAgreement)
            .filter(PaymentAgreement.admission_id == admission_id)
            .first()
        )

    def upsert_agreement(self, admission_id: int, data: PaymentAgreementUpsert) -> PaymentAgreement:
        agreement = self.get_agreement(admission_id)
        if agreement:
            for field, val in data.model_dump().items():
                setattr(agreement, field, val)
        else:
            agreement = PaymentAgreement(admission_id=admission_id, **data.model_dump())
            self.db.add(agreement)
        self.db.commit()
        self.db.refresh(agreement)
        return agreement

    # ------------------------------------------------------------------ #
    # Charges
    # ------------------------------------------------------------------ #

    def list_charges(self, admission_id: int) -> List[Charge]:
        return (
            self.db.query(Charge)
            .filter(Charge.admission_id == admission_id)
            .order_by(Charge.charge_date.asc())
            .all()
        )

    def create_charge(
        self, admission_id: int, data: ChargeCreate, created_by_user_id: Optional[int] = None
    ) -> Charge:
        charge = Charge(
            admission_id=admission_id,
            is_auto=False,
            created_by_user_id=created_by_user_id,
            **data.model_dump(),
        )
        self.db.add(charge)
        self.db.commit()
        self.db.refresh(charge)
        return charge

    def delete_charge(self, charge_id: int) -> None:
        charge = self.db.query(Charge).filter(Charge.id == charge_id).first()
        if not charge:
            raise HTTPException(status_code=404, detail="Cargo no encontrado")
        self.db.delete(charge)
        self.db.commit()

    # ------------------------------------------------------------------ #
    # Payments
    # ------------------------------------------------------------------ #

    def list_payments(self, admission_id: int) -> List[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.admission_id == admission_id)
            .order_by(Payment.payment_date.asc())
            .all()
        )

    def create_payment(self, admission_id: int, data: PaymentCreate) -> Payment:
        max_receipt = self.db.query(func.max(Payment.receipt_number)).scalar() or 0
        payment = Payment(
            admission_id=admission_id,
            receipt_number=max_receipt + 1,
            **data.model_dump(),
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    # ------------------------------------------------------------------ #
    # Account (cuenta corriente)
    # ------------------------------------------------------------------ #

    def get_account(self, admission_id: int) -> AccountOut:
        charges = self.list_charges(admission_id)
        payments = self.list_payments(admission_id)
        total_charges = sum((c.amount for c in charges), Decimal(0))
        total_payments = sum((p.amount for p in payments), Decimal(0))
        return AccountOut(
            charges=[ChargeOut.model_validate(c) for c in charges],
            payments=[PaymentOut.model_validate(p) for p in payments],
            balance=total_charges - total_payments,
        )

    # ------------------------------------------------------------------ #
    # Monthly charge generation
    # ------------------------------------------------------------------ #

    def generate_monthly_charges(self, period: str) -> List[Charge]:
        """Idempotente: omite si ya existe un cargo para (admission, period)."""
        year = int(period[:4])
        month = int(period[5:7])

        agreements = (
            self.db.query(PaymentAgreement)
            .join(Admission, PaymentAgreement.admission_id == Admission.id)
            .filter(
                PaymentAgreement.agreement_type == AgreementType.monthly,
                PaymentAgreement.is_active == True,  # noqa: E712
                Admission.status.in_(ACTIVE_STATUSES),
                Admission.is_deleted == False,  # noqa: E712
            )
            .all()
        )

        # Pre-fetch existing periods to avoid per-admission queries
        admission_ids = [a.admission_id for a in agreements]
        existing = set(
            row[0]
            for row in self.db.query(Charge.admission_id)
            .filter(Charge.admission_id.in_(admission_ids), Charge.period == period)
            .all()
        )

        max_day = calendar.monthrange(year, month)[1]
        concept = f"Mensualidad {MONTH_NAMES_ES[month - 1]} {year}"
        created: List[Charge] = []

        for agreement in agreements:
            if agreement.admission_id in existing:
                continue
            billing_day = min(agreement.billing_day or 1, max_day)
            charge = Charge(
                admission_id=agreement.admission_id,
                concept=concept,
                amount=agreement.amount,
                charge_date=date(year, month, billing_day),
                period=period,
                is_auto=True,
            )
            self.db.add(charge)
            created.append(charge)

        if created:
            self.db.commit()
            for c in created:
                self.db.refresh(c)

        return created

    # ------------------------------------------------------------------ #
    # Overdue list
    # ------------------------------------------------------------------ #

    def get_overdue(self, margin_days: int = 30) -> List[OverdueEntryOut]:
        today = date.today()
        cutoff = today - timedelta(days=margin_days)

        admissions = (
            self.db.query(Admission)
            .options(
                joinedload(Admission.resident),
                joinedload(Admission.charges),
                joinedload(Admission.payments),
            )
            .filter(
                Admission.status.in_(ACTIVE_STATUSES),
                Admission.is_deleted == False,  # noqa: E712
            )
            .all()
        )

        results: List[OverdueEntryOut] = []
        for admission in admissions:
            if not admission.charges:
                continue
            total_charges = sum((c.amount for c in admission.charges), Decimal(0))
            total_payments = sum((p.amount for p in admission.payments), Decimal(0))
            balance = total_charges - total_payments
            if balance <= 0:
                continue
            oldest = min(c.charge_date for c in admission.charges)
            if oldest > cutoff:
                continue
            resident: Resident = admission.resident
            results.append(
                OverdueEntryOut(
                    admission_id=admission.id,
                    resident_name=f"{resident.first_name} {resident.last_name}",
                    balance=balance,
                    oldest_charge_date=oldest,
                    days_overdue=(today - oldest).days,
                )
            )

        results.sort(key=lambda x: x.days_overdue, reverse=True)
        return results

    # ------------------------------------------------------------------ #
    # PDF context helpers
    # ------------------------------------------------------------------ #

    def get_payment_for_receipt(self, payment_id: int) -> Payment:
        payment = (
            self.db.query(Payment)
            .options(
                joinedload(Payment.admission).joinedload(Admission.resident),
                joinedload(Payment.received_by),
            )
            .filter(Payment.id == payment_id)
            .first()
        )
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return payment

    def get_statement_context(self, admission_id: int) -> dict:
        admission = (
            self.db.query(Admission)
            .options(joinedload(Admission.resident))
            .filter(Admission.id == admission_id)
            .first()
        )
        if not admission:
            raise HTTPException(status_code=404, detail="Admisión no encontrada")
        account = self.get_account(admission_id)
        agreement = self.get_agreement(admission_id)
        return {
            "admission": admission,
            "resident": admission.resident,
            "agreement": agreement,
            "account": account,
        }

    # ------------------------------------------------------------------ #
    # Overview dashboard
    # ------------------------------------------------------------------ #

    def get_overview(self, period: str) -> FinanceOverviewOut:
        year = int(period[:4])
        month = int(period[5:7])
        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])

        payments = (
            self.db.query(Payment)
            .filter(Payment.payment_date >= start, Payment.payment_date <= end)
            .all()
        )

        total_received = sum((p.amount for p in payments), Decimal(0))
        by_payer: dict[str, Decimal] = {}
        for p in payments:
            key = p.payer_type.value
            by_payer[key] = by_payer.get(key, Decimal(0)) + p.amount

        overdue = self.get_overdue()
        overdue_total = sum((e.balance for e in overdue), Decimal(0))

        return FinanceOverviewOut(
            period=period,
            total_received=total_received,
            by_payer_type=by_payer,
            overdue_count=len(overdue),
            overdue_total=overdue_total,
        )
