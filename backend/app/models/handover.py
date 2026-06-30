"""
Modelos de entrega de turno (shift handover).

Ventanas de turno:
  morning:   06:00–14:00
  afternoon: 14:00–22:00
  night:     22:00–06:00 (día siguiente)
"""
import enum
from datetime import date, datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum,
    ForeignKey, Integer, String, Text, UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.attendance import Shift  # reusar, no redefinir


class HandoverStatus(str, enum.Enum):
    open = "open"
    closed = "closed"
    received = "received"


class IncidentSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ShiftHandover(Base):
    __tablename__ = "shift_handovers"
    __table_args__ = (UniqueConstraint("date", "shift", name="uq_shift_handover_date_shift"),)

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    shift = Column(SAEnum(Shift, name="shift", create_type=False), nullable=False)
    auto_summary = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    closed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    received_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SAEnum(HandoverStatus, name="handoverstatus"), nullable=False, default=HandoverStatus.open)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    closed_by = relationship("User", foreign_keys=[closed_by_user_id])
    received_by = relationship("User", foreign_keys=[received_by_user_id])
    incidents = relationship("ShiftIncident", back_populates="handover", cascade="all, delete-orphan")
    tasks = relationship("ShiftTask", back_populates="handover", cascade="all, delete-orphan")


class ShiftIncident(Base):
    __tablename__ = "shift_incidents"

    id = Column(Integer, primary_key=True, index=True)
    handover_id = Column(Integer, ForeignKey("shift_handovers.id"), nullable=False)
    admission_id = Column(Integer, ForeignKey("admissions.id"), nullable=True)
    type = Column(String, nullable=False)
    severity = Column(SAEnum(IncidentSeverity, name="incidentseverity"), nullable=False)
    description = Column(Text, nullable=False)
    action_taken = Column(Text, nullable=True)
    reported_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    handover = relationship("ShiftHandover", back_populates="incidents")
    admission = relationship("Admission", foreign_keys=[admission_id])
    reported_by = relationship("User", foreign_keys=[reported_by_user_id])


class ShiftTask(Base):
    __tablename__ = "shift_tasks"

    id = Column(Integer, primary_key=True, index=True)
    handover_id = Column(Integer, ForeignKey("shift_handovers.id"), nullable=False)
    related_admission_id = Column(Integer, ForeignKey("admissions.id"), nullable=True)
    description = Column(Text, nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=True)
    is_done = Column(Boolean, nullable=False, default=False)
    done_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    handover = relationship("ShiftHandover", back_populates="tasks")
    related_admission = relationship("Admission", foreign_keys=[related_admission_id])
    done_by = relationship("User", foreign_keys=[done_by_user_id])
