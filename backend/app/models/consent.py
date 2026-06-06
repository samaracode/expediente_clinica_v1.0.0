import enum
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ConsentType(str, enum.Enum):
    internment_service = "INTERNMENT_SERVICE"
    internment = "INTERNMENT"
    search = "SEARCH"
    drug_test = "DRUG_TEST"
    cctv = "CCTV"
    info_release = "INFO_RELEASE"
    weapons = "WEAPONS"
    iafa_actions = "IAFA_ACTIONS"
    individual_approach = "INDIVIDUAL_APPROACH"
    referral = "REFERRAL"
    record_access = "RECORD_ACCESS"
    rights_focus = "RIGHTS_FOCUS"
    labor = "LABOR"
    non_discrimination = "NON_DISCRIMINATION"
    sponsor = "SPONSOR"
    manual = "MANUAL"
    labor_provision = "LABOR_PROVISION"


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    consent_type = sa.Column(sa.Enum(ConsentType), nullable=False)
    is_signed = sa.Column(sa.Boolean, default=False, nullable=False)
    signed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    verified_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    authorized_persons = sa.Column(postgresql.JSONB, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    file_id = sa.Column(sa.Integer, sa.ForeignKey("files.id"), nullable=True)

    admission = relationship("Admission", back_populates="consent_records")
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])


class PersonalItemsInventory(Base):
    __tablename__ = "personal_items_inventories"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    recorded_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    recorded_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    items = sa.Column(postgresql.JSONB, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    user_signature_file_id = sa.Column(sa.Integer, sa.ForeignKey("files.id"), nullable=True)
    staff_signature_file_id = sa.Column(sa.Integer, sa.ForeignKey("files.id"), nullable=True)

    admission = relationship("Admission", back_populates="personal_items_inventory")
    recorded_by = relationship("User", foreign_keys=[recorded_by_user_id])
