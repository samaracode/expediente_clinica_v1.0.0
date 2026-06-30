from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.finance import AgreementType, PayerType, PaymentMethod


# ---------------------------------------------------------------------------
# Payment Agreement
# ---------------------------------------------------------------------------

class PaymentAgreementUpsert(BaseModel):
    agreement_type: AgreementType
    amount: Decimal
    billing_day: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool = True


class PaymentAgreementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admission_id: int
    agreement_type: AgreementType
    amount: Decimal
    billing_day: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Charges
# ---------------------------------------------------------------------------

class ChargeCreate(BaseModel):
    concept: str
    amount: Decimal
    charge_date: date
    period: Optional[str] = None
    notes: Optional[str] = None


class ChargeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admission_id: int
    concept: str
    amount: Decimal
    charge_date: date
    period: Optional[str] = None
    is_auto: bool
    created_by_user_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

class PaymentCreate(BaseModel):
    amount: Decimal
    payment_date: date
    method: PaymentMethod
    payer_type: PayerType
    payer_name: Optional[str] = None
    reference: Optional[str] = None
    received_by_user_id: Optional[int] = None
    notes: Optional[str] = None


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admission_id: int
    amount: Decimal
    payment_date: date
    method: PaymentMethod
    payer_type: PayerType
    payer_name: Optional[str] = None
    reference: Optional[str] = None
    receipt_number: int
    received_by_user_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Account (saldo de cuenta corriente)
# ---------------------------------------------------------------------------

class AccountOut(BaseModel):
    charges: List[ChargeOut]
    payments: List[PaymentOut]
    balance: Decimal  # Σcharges − Σpayments; positive = owes money


# ---------------------------------------------------------------------------
# Overdue list
# ---------------------------------------------------------------------------

class OverdueEntryOut(BaseModel):
    admission_id: int
    resident_name: str
    balance: Decimal
    oldest_charge_date: date
    days_overdue: int


# ---------------------------------------------------------------------------
# Finance overview dashboard
# ---------------------------------------------------------------------------

class FinanceOverviewOut(BaseModel):
    period: str  # "YYYY-MM"
    total_received: Decimal
    by_payer_type: Dict[str, Decimal]
    overdue_count: int
    overdue_total: Decimal
