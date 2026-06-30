import enum
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class OperationType(str, enum.Enum):
    create = "CREATE"
    update = "UPDATE"
    delete = "DELETE"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    operation_type = sa.Column(sa.Enum(OperationType), nullable=False)
    table_affected = sa.Column(sa.String, nullable=False)
    record_id = sa.Column(sa.Integer, nullable=True)
    timestamp = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    user = relationship("User", foreign_keys=[user_id])


class ProgramAbandonment(Base):
    __tablename__ = "program_abandonments"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    abandoned_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    reason = sa.Column(sa.Text, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    staff_notified_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)

    admission = relationship("Admission", back_populates="program_abandonment")
    staff_notified = relationship("User", foreign_keys=[staff_notified_id])


class Complaint(Base):
    __tablename__ = "complaints"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    reported_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    description = sa.Column(sa.Text, nullable=False)
    resolution = sa.Column(sa.Text, nullable=True)
    resolved_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    resolved_by_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)

    admission = relationship("Admission", back_populates="complaints")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
