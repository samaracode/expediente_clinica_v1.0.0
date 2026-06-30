"""
Tests para FinanceService.
Nivel de servicio; sin capa HTTP, igual que el resto del suite.
"""

from datetime import date
from decimal import Decimal

import pytest

from app.models.admission import AdmissionStatus
from app.models.finance import AgreementType, PaymentMethod, PayerType
from app.schemas.finance import (
    ChargeCreate,
    PaymentAgreementUpsert,
    PaymentCreate,
)
from app.services.finance_service import FinanceService


# ─── Helpers ────────────────────────────────────────────────────────────────

def _svc(db):
    return FinanceService(db)


def _monthly_agreement(amount="500000.00", billing_day=None):
    return PaymentAgreementUpsert(
        agreement_type=AgreementType.monthly,
        amount=Decimal(amount),
        billing_day=billing_day,
        is_active=True,
    )


def _charge(concept="Depósito", amount="100000.00", charge_date=None):
    return ChargeCreate(
        concept=concept,
        amount=Decimal(amount),
        charge_date=charge_date or date(2026, 1, 1),
    )


def _payment(amount="100000.00", payment_date=None):
    return PaymentCreate(
        amount=Decimal(amount),
        payment_date=payment_date or date(2026, 1, 15),
        method=PaymentMethod.sinpe,
        payer_type=PayerType.family,
    )


# ─── Agreement ──────────────────────────────────────────────────────────────

def test_upsert_agreement_creates(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    agreement = svc.upsert_agreement(admission.id, _monthly_agreement())
    assert agreement.id is not None
    assert agreement.admission_id == admission.id
    assert agreement.agreement_type == AgreementType.monthly
    assert agreement.amount == Decimal("500000.00")


def test_upsert_agreement_updates(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    svc.upsert_agreement(admission.id, _monthly_agreement("500000.00"))
    updated = svc.upsert_agreement(
        admission.id,
        PaymentAgreementUpsert(
            agreement_type=AgreementType.scholarship_partial,
            amount=Decimal("250000.00"),
            is_active=True,
        ),
    )
    assert updated.agreement_type == AgreementType.scholarship_partial
    assert updated.amount == Decimal("250000.00")
    # Only one row per admission
    from app.models.finance import PaymentAgreement
    count = db.query(PaymentAgreement).filter_by(admission_id=admission.id).count()
    assert count == 1


def test_get_agreement_returns_none_when_missing(db, make_admission):
    admission = make_admission()
    assert _svc(db).get_agreement(admission.id) is None


# ─── Charges ────────────────────────────────────────────────────────────────

def test_create_manual_charge(db, make_admission, make_user):
    admission = make_admission()
    user = make_user()
    svc = _svc(db)
    charge = svc.create_charge(admission.id, _charge(), created_by_user_id=user.id)
    assert charge.id is not None
    assert charge.is_auto is False
    assert charge.created_by_user_id == user.id
    assert charge.admission_id == admission.id


def test_list_charges_ordered_by_date(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    svc.create_charge(admission.id, _charge(charge_date=date(2026, 3, 1)))
    svc.create_charge(admission.id, _charge(charge_date=date(2026, 1, 1)))
    charges = svc.list_charges(admission.id)
    assert charges[0].charge_date <= charges[1].charge_date


def test_delete_charge(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    charge = svc.create_charge(admission.id, _charge())
    svc.delete_charge(charge.id)
    assert svc.list_charges(admission.id) == []


def test_delete_charge_not_found(db):
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        _svc(db).delete_charge(99999)
    assert exc.value.status_code == 404


# ─── Payments ───────────────────────────────────────────────────────────────

def test_create_payment_assigns_receipt_number(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    p1 = svc.create_payment(admission.id, _payment())
    p2 = svc.create_payment(admission.id, _payment())
    assert p1.receipt_number == 1
    assert p2.receipt_number == 2


def test_receipt_numbers_global_across_admissions(db, make_admission):
    a1 = make_admission()
    a2 = make_admission()
    svc = _svc(db)
    p1 = svc.create_payment(a1.id, _payment())
    p2 = svc.create_payment(a2.id, _payment())
    assert p1.receipt_number == 1
    assert p2.receipt_number == 2


def test_list_payments(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    svc.create_payment(admission.id, _payment())
    svc.create_payment(admission.id, _payment())
    assert len(svc.list_payments(admission.id)) == 2


# ─── Account ────────────────────────────────────────────────────────────────

def test_get_account_balance(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    svc.create_charge(admission.id, _charge(amount="600000.00"))
    svc.create_payment(admission.id, _payment(amount="200000.00"))
    account = svc.get_account(admission.id)
    assert account.balance == Decimal("400000.00")


def test_get_account_zero_balance_when_paid(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    svc.create_charge(admission.id, _charge(amount="300000.00"))
    svc.create_payment(admission.id, _payment(amount="300000.00"))
    account = svc.get_account(admission.id)
    assert account.balance == Decimal("0.00")


def test_get_account_no_charges(db, make_admission):
    admission = make_admission()
    account = _svc(db).get_account(admission.id)
    assert account.balance == Decimal("0")
    assert account.charges == []
    assert account.payments == []


# ─── Monthly charge generation ──────────────────────────────────────────────

def test_generate_monthly_charges_creates_for_active_admissions(db, make_admission):
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    svc.upsert_agreement(admission.id, _monthly_agreement("500000.00", billing_day=5))
    created = svc.generate_monthly_charges("2026-06")
    assert len(created) == 1
    assert created[0].is_auto is True
    assert created[0].period == "2026-06"
    assert created[0].charge_date == date(2026, 6, 5)
    assert "junio" in created[0].concept


def test_generate_monthly_charges_idempotent(db, make_admission):
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    svc.upsert_agreement(admission.id, _monthly_agreement())
    first = svc.generate_monthly_charges("2026-06")
    second = svc.generate_monthly_charges("2026-06")
    assert len(first) == 1
    assert len(second) == 0  # already exists


def test_generate_monthly_charges_skips_inactive_admissions(db, make_admission):
    admission = make_admission(status=AdmissionStatus.discharged)
    svc = _svc(db)
    svc.upsert_agreement(admission.id, _monthly_agreement())
    created = svc.generate_monthly_charges("2026-06")
    assert created == []


def test_generate_monthly_charges_billing_day_clamped(db, make_admission):
    """billing_day=31 en un mes de 30 días → día 30"""
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    svc.upsert_agreement(admission.id, _monthly_agreement(billing_day=31))
    created = svc.generate_monthly_charges("2026-06")  # junio tiene 30 días
    assert created[0].charge_date.day == 30


def test_generate_monthly_charges_default_billing_day_is_1(db, make_admission):
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    svc.upsert_agreement(admission.id, _monthly_agreement(billing_day=None))
    created = svc.generate_monthly_charges("2026-06")
    assert created[0].charge_date.day == 1


def test_generate_monthly_charges_skips_non_monthly_agreements(db, make_admission):
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    svc.upsert_agreement(
        admission.id,
        PaymentAgreementUpsert(
            agreement_type=AgreementType.fixed_total,
            amount=Decimal("2000000.00"),
            is_active=True,
        ),
    )
    created = svc.generate_monthly_charges("2026-06")
    assert created == []


# ─── Overdue ────────────────────────────────────────────────────────────────

def test_get_overdue_returns_entry_past_margin(db, make_admission):
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    svc.create_charge(admission.id, _charge(amount="500000.00", charge_date=date(2026, 1, 1)))
    overdue = svc.get_overdue(margin_days=30)
    assert len(overdue) == 1
    assert overdue[0].admission_id == admission.id
    assert overdue[0].balance == Decimal("500000.00")


def test_get_overdue_excludes_paid_admissions(db, make_admission):
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    svc.create_charge(admission.id, _charge(amount="300000.00", charge_date=date(2026, 1, 1)))
    svc.create_payment(admission.id, _payment(amount="300000.00"))
    assert svc.get_overdue(margin_days=30) == []


def test_get_overdue_excludes_recent_charges(db, make_admission):
    """Charge más reciente que el margen → no es moroso"""
    admission = make_admission(status=AdmissionStatus.treatment_active)
    svc = _svc(db)
    today = date.today()
    svc.create_charge(admission.id, _charge(amount="300000.00", charge_date=today))
    assert svc.get_overdue(margin_days=30) == []


def test_get_overdue_excludes_inactive_admissions(db, make_admission):
    admission = make_admission(status=AdmissionStatus.discharged)
    svc = _svc(db)
    svc.create_charge(admission.id, _charge(amount="300000.00", charge_date=date(2026, 1, 1)))
    assert svc.get_overdue(margin_days=30) == []


# ─── Overview ────────────────────────────────────────────────────────────────

def test_get_overview_totals(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    svc.create_payment(admission.id, PaymentCreate(
        amount=Decimal("200000.00"),
        payment_date=date(2026, 6, 10),
        method=PaymentMethod.cash,
        payer_type=PayerType.family,
    ))
    svc.create_payment(admission.id, PaymentCreate(
        amount=Decimal("100000.00"),
        payment_date=date(2026, 6, 20),
        method=PaymentMethod.sinpe,
        payer_type=PayerType.iafa,
    ))
    overview = svc.get_overview("2026-06")
    assert overview.period == "2026-06"
    assert overview.total_received == Decimal("300000.00")
    assert overview.by_payer_type["family"] == Decimal("200000.00")
    assert overview.by_payer_type["iafa"] == Decimal("100000.00")


def test_get_overview_excludes_other_months(db, make_admission):
    admission = make_admission()
    svc = _svc(db)
    svc.create_payment(admission.id, PaymentCreate(
        amount=Decimal("500000.00"),
        payment_date=date(2026, 5, 15),  # mayo, no junio
        method=PaymentMethod.transfer,
        payer_type=PayerType.family,
    ))
    overview = svc.get_overview("2026-06")
    assert overview.total_received == Decimal("0")
