import enum
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Shift(str, enum.Enum):
    morning = "morning"
    afternoon = "afternoon"
    night = "night"


class PresenceStatus(str, enum.Enum):
    present = "present"
    on_pass = "on_pass"
    external_appointment = "external_appointment"
    hospitalized = "hospitalized"
    absent_without_leave = "absent_without_leave"
    discharged = "discharged"


class AttendanceRollCall(Base):
    __tablename__ = "attendance_roll_calls"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    date = sa.Column(sa.Date, nullable=False)
    shift = sa.Column(sa.Enum(Shift), nullable=False)
    conducted_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    conducted_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    notes = sa.Column(sa.Text, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint("date", "shift", name="uq_roll_call_date_shift"),
    )

    conducted_by = relationship("User", foreign_keys=[conducted_by_user_id])
    entries = relationship(
        "AttendanceEntry",
        back_populates="roll_call",
        cascade="all, delete-orphan",
    )


class AttendanceEntry(Base):
    __tablename__ = "attendance_entries"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    roll_call_id = sa.Column(
        sa.Integer, sa.ForeignKey("attendance_roll_calls.id"), nullable=False
    )
    admission_id = sa.Column(
        sa.Integer, sa.ForeignKey("admissions.id"), nullable=False
    )
    expected_status = sa.Column(sa.Enum(PresenceStatus), nullable=False)
    actual_status = sa.Column(sa.Enum(PresenceStatus), nullable=False)
    note = sa.Column(sa.Text, nullable=True)

    roll_call = relationship("AttendanceRollCall", back_populates="entries")
    admission = relationship("Admission", back_populates="attendance_entries")
