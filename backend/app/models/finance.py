import enum
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class AgreementType(str, enum.Enum):
    monthly = "monthly"
    fixed_total = "fixed_total"
    scholarship_full = "scholarship_full"
    scholarship_partial = "scholarship_partial"


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    sinpe = "sinpe"
    transfer = "transfer"
    check = "check"
    other = "other"


class PayerType(str, enum.Enum):
    family = "family"
    iafa = "iafa"
    imas = "imas"
    church = "church"
    donor = "donor"
    other = "other"


class PaymentAgreement(Base):
    __tablename__ = "payment_agreements"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    agreement_type = sa.Column(sa.Enum(AgreementType), nullable=False)
    amount = sa.Column(sa.Numeric(12, 2), nullable=False)
    billing_day = sa.Column(sa.Integer, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    is_active = sa.Column(sa.Boolean, nullable=False, default=True, server_default="true")
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    admission = relationship("Admission", back_populates="payment_agreement")


class Charge(Base):
    __tablename__ = "charges"
    __table_args__ = (
        # Partial unique index: prevents duplicate monthly period per admission.
        # Rows with period=NULL (manual charges) are excluded and never conflict.
        # postgresql_where is ignored by SQLite (tests), which allows multiple NULLs anyway.
        sa.Index("uq_charges_admission_period", "admission_id", "period", unique=True,
                 postgresql_where=sa.text("period IS NOT NULL")),
    )

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    concept = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Numeric(12, 2), nullable=False)
    charge_date = sa.Column(sa.Date, nullable=False)
    period = sa.Column(sa.String(7), nullable=True)  # "YYYY-MM" for monthly auto-charges
    is_auto = sa.Column(sa.Boolean, nullable=False, default=False, server_default="false")
    created_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    admission = relationship("Admission", back_populates="charges")
    created_by = relationship("User", foreign_keys=[created_by_user_id])


class Payment(Base):
    __tablename__ = "payments"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    amount = sa.Column(sa.Numeric(12, 2), nullable=False)
    payment_date = sa.Column(sa.Date, nullable=False)
    method = sa.Column(sa.Enum(PaymentMethod), nullable=False)
    payer_type = sa.Column(sa.Enum(PayerType), nullable=False)
    payer_name = sa.Column(sa.String, nullable=True)
    reference = sa.Column(sa.String, nullable=True)
    receipt_number = sa.Column(sa.Integer, nullable=False, unique=True)
    received_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    admission = relationship("Admission", back_populates="payments")
    received_by = relationship("User", foreign_keys=[received_by_user_id])
