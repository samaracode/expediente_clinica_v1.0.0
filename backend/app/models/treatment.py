import enum
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class StageStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    extended = "extended"


class StageName(str, enum.Enum):
    orientation = "orientation"
    adaptation = "adaptation"
    development = "development"
    consolidation = "consolidation"
    reintegration = "reintegration"


class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    created_by_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    recommendations = sa.Column(sa.Text, nullable=True)
    plan_details = sa.Column(sa.Text, nullable=True)
    life_project = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    admission = relationship("Admission", back_populates="treatment_plan")
    created_by = relationship("User", foreign_keys=[created_by_id])
    stages = relationship("TreatmentStage", back_populates="treatment_plan", order_by="TreatmentStage.stage_order")


class TreatmentStage(Base):
    __tablename__ = "treatment_stages"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    treatment_plan_id = sa.Column(sa.Integer, sa.ForeignKey("treatment_plans.id"), nullable=False)
    stage_name = sa.Column(sa.Enum(StageName), nullable=False)
    stage_order = sa.Column(sa.Integer, nullable=False)
    start_date = sa.Column(sa.Date, nullable=True)
    end_date = sa.Column(sa.Date, nullable=True)
    progress_notes = sa.Column(sa.Text, nullable=True)
    extension_consent_signed = sa.Column(sa.Boolean, default=False)
    advancement_criteria = sa.Column(sa.Text, nullable=True)
    status = sa.Column(sa.Enum(StageStatus), nullable=False, default=StageStatus.pending)

    treatment_plan = relationship("TreatmentPlan", back_populates="stages")
