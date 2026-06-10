import enum
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class PassStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"


class PassType(str, enum.Enum):
    regular = "regular"
    special = "special"


class ExitPass(Base):
    __tablename__ = "exit_passes"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    requested_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    approved_by_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    departure_date = sa.Column(sa.DateTime(timezone=True), nullable=True)
    return_date_expected = sa.Column(sa.DateTime(timezone=True), nullable=True)
    return_date_actual = sa.Column(sa.DateTime(timezone=True), nullable=True)
    reason = sa.Column(sa.Text, nullable=True)
    narrative = sa.Column(sa.Text, nullable=True)
    companion = sa.Column(sa.String, nullable=True)
    pass_type = sa.Column(sa.Enum(PassType), nullable=False, default=PassType.regular)
    status = sa.Column(sa.Enum(PassStatus), nullable=False, default=PassStatus.pending)

    admission = relationship("Admission", back_populates="exit_passes")
    approved_by = relationship("User", foreign_keys=[approved_by_id])


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    logged_by_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    log_date = sa.Column(sa.Date, nullable=False)
    intervention_type = sa.Column(sa.String, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    recommendations = sa.Column(sa.Text, nullable=True)
    is_deleted = sa.Column(sa.Boolean, nullable=False, default=False, server_default="false")
    deleted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    admission = relationship("Admission", back_populates="daily_logs")
    logged_by = relationship("User", foreign_keys=[logged_by_id])


class FamilyTherapySession(Base):
    __tablename__ = "family_therapy_sessions"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    therapist_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    session_date = sa.Column(sa.Date, nullable=False)
    attendees = sa.Column(postgresql.JSONB, nullable=True)
    session_type = sa.Column(sa.String, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)

    admission = relationship("Admission", back_populates="family_therapy_sessions")
    therapist = relationship("User", foreign_keys=[therapist_id])


class Consultation(Base):
    __tablename__ = "consultations"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    professional_id = sa.Column(sa.Integer, sa.ForeignKey("professionals.id"), nullable=True)
    area_id = sa.Column(sa.Integer, sa.ForeignKey("treatment_areas.id"), nullable=True)
    consultation_type = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.Text, nullable=True)
    observations = sa.Column(sa.Text, nullable=True)
    next_appointment_date = sa.Column(sa.Date, nullable=True)
    consultation_date = sa.Column(sa.Date, nullable=False)
    is_deleted = sa.Column(sa.Boolean, nullable=False, default=False, server_default="false")
    deleted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    admission = relationship("Admission", back_populates="consultations")
    professional = relationship("Professional", foreign_keys=[professional_id])
    area = relationship("TreatmentArea", foreign_keys=[area_id])
