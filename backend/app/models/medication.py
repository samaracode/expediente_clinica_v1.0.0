import enum
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class MedicationRoute(str, enum.Enum):
    oral = "oral"
    im = "im"
    sc = "sc"
    other = "other"


class ScheduleType(str, enum.Enum):
    scheduled = "scheduled"
    prn = "prn"


class OrderStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    finished = "finished"


class AdministrationStatus(str, enum.Enum):
    pending = "pending"
    taken = "taken"
    refused = "refused"
    omitted = "omitted"


class AllergySeverity(str, enum.Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"


class Medication(Base):
    __tablename__ = "medications"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, nullable=False)
    form = sa.Column(sa.String, nullable=True)
    strength = sa.Column(sa.String, nullable=True)
    is_controlled = sa.Column(sa.Boolean, default=False, nullable=False)
    notes = sa.Column(sa.Text, nullable=True)

    orders = relationship("MedicationOrder", back_populates="medication")


class MedicationOrder(Base):
    __tablename__ = "medication_orders"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    medication_id = sa.Column(sa.Integer, sa.ForeignKey("medications.id"), nullable=False)
    dose = sa.Column(sa.String, nullable=False)
    route = sa.Column(sa.Enum(MedicationRoute), nullable=False)
    schedule_type = sa.Column(sa.Enum(ScheduleType), nullable=False)
    times = sa.Column(postgresql.JSONB, nullable=True)
    frequency_text = sa.Column(sa.String, nullable=True)
    prn_reason = sa.Column(sa.Text, nullable=True)
    start_date = sa.Column(sa.Date, nullable=False)
    end_date = sa.Column(sa.Date, nullable=True)
    prescribed_by_external = sa.Column(sa.String, nullable=True)
    prescriber_institution = sa.Column(sa.String, nullable=True)
    transcribed_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    receta_file_id = sa.Column(sa.Integer, sa.ForeignKey("files.id"), nullable=True)
    is_controlled = sa.Column(sa.Boolean, default=False, nullable=False)
    status = sa.Column(sa.Enum(OrderStatus), nullable=False, default=OrderStatus.active)
    notes = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    admission = relationship("Admission", back_populates="medication_orders")
    medication = relationship("Medication", back_populates="orders")
    transcribed_by = relationship("User", foreign_keys=[transcribed_by_user_id])
    receta_file = relationship("File", foreign_keys=[receta_file_id])
    administrations = relationship("MedicationAdministration", back_populates="order")


class MedicationAdministration(Base):
    __tablename__ = "medication_administrations"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    order_id = sa.Column(sa.Integer, sa.ForeignKey("medication_orders.id"), nullable=False)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    scheduled_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    status = sa.Column(
        sa.Enum(AdministrationStatus), nullable=False, default=AdministrationStatus.pending
    )
    administered_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    administered_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    witness_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    reason = sa.Column(sa.Text, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    order = relationship("MedicationOrder", back_populates="administrations")
    admission = relationship("Admission", back_populates="medication_administrations")
    administered_by = relationship("User", foreign_keys=[administered_by_user_id])
    witness = relationship("User", foreign_keys=[witness_user_id])


class MedTimeSlot(Base):
    __tablename__ = "med_time_slots"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    label = sa.Column(sa.String, nullable=False)
    time = sa.Column(sa.Time, nullable=False)
    sort_order = sa.Column(sa.Integer, default=0, nullable=False)


class ResidentAllergy(Base):
    __tablename__ = "resident_allergies"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    resident_id = sa.Column(sa.Integer, sa.ForeignKey("residents.id"), nullable=False)
    substance = sa.Column(sa.String, nullable=False)
    reaction = sa.Column(sa.String, nullable=True)
    severity = sa.Column(sa.Enum(AllergySeverity), nullable=True)

    resident = relationship("Resident", back_populates="allergies")
