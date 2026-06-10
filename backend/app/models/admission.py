import enum
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class AdmissionStatus(str, enum.Enum):
    intake_pending = "intake_pending"
    consents_pending = "consents_pending"
    assessment_in_progress = "assessment_in_progress"
    treatment_active = "treatment_active"
    discharged = "discharged"
    abandoned = "abandoned"


class AdmissionType(str, enum.Enum):
    first = "first"
    readmission = "readmission"


class Admission(Base):
    __tablename__ = "admissions"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    resident_id = sa.Column(sa.Integer, sa.ForeignKey("residents.id"), nullable=False)
    admission_number = sa.Column(sa.String, unique=True, nullable=False, index=True)
    admission_type = sa.Column(sa.Enum(AdmissionType), nullable=False, default=AdmissionType.first)
    admission_date = sa.Column(sa.Date, nullable=False)
    discharge_date = sa.Column(sa.Date, nullable=True)
    discharge_reason = sa.Column(sa.String, nullable=True)
    assigned_counselor_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    status = sa.Column(sa.Enum(AdmissionStatus), nullable=False, default=AdmissionStatus.intake_pending)
    referral_source = sa.Column(sa.String, nullable=True)
    admission_condition = sa.Column(sa.Text, nullable=True)
    initial_diagnosis = sa.Column(sa.Text, nullable=True)
    sponsor_name = sa.Column(sa.String, nullable=True)
    sponsor_relationship = sa.Column(sa.String, nullable=True)
    sponsor_phone = sa.Column(sa.String, nullable=True)
    sponsor_address = sa.Column(sa.Text, nullable=True)
    judicial_status = sa.Column(sa.String, nullable=True)
    has_support_network = sa.Column(sa.Boolean, default=False)
    is_deleted = sa.Column(sa.Boolean, nullable=False, default=False, server_default="false")
    deleted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    resident = relationship("Resident", back_populates="admissions")
    assigned_counselor = relationship("User", foreign_keys=[assigned_counselor_id])
    economic_situation = relationship("EconomicSituation", back_populates="admission", uselist=False)
    household_members = relationship("HouseholdMember", back_populates="admission")
    consumption_snapshot = relationship("ConsumptionSnapshot", back_populates="admission", uselist=False)
    consent_records = relationship("ConsentRecord", back_populates="admission")
    personal_items_inventory = relationship("PersonalItemsInventory", back_populates="admission", uselist=False)
    medical_record = relationship("MedicalRecord", back_populates="admission", uselist=False)
    therapeutic_assessment = relationship("TherapeuticAssessment", back_populates="admission", uselist=False)
    social_work_assessment = relationship("SocialWorkAssessment", back_populates="admission", uselist=False)
    psychology_assessment = relationship("PsychologyAssessment", back_populates="admission", uselist=False)
    occupational_therapy_assessment = relationship("OccupationalTherapyAssessment", back_populates="admission", uselist=False)
    treatment_plan = relationship("TreatmentPlan", back_populates="admission", uselist=False)
    exit_passes = relationship("ExitPass", back_populates="admission")
    daily_logs = relationship("DailyLog", back_populates="admission")
    family_therapy_sessions = relationship("FamilyTherapySession", back_populates="admission")
    consultations = relationship("Consultation", back_populates="admission")
    program_abandonment = relationship("ProgramAbandonment", back_populates="admission", uselist=False)
    complaints = relationship("Complaint", back_populates="admission")


class EconomicSituation(Base):
    __tablename__ = "economic_situations"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    has_worked = sa.Column(sa.Boolean, nullable=True)
    current_job = sa.Column(sa.String, nullable=True)
    work_phone = sa.Column(sa.String, nullable=True)
    workplace = sa.Column(sa.String, nullable=True)
    job_title = sa.Column(sa.String, nullable=True)
    tenure_months = sa.Column(sa.Integer, nullable=True)
    monthly_income_colones = sa.Column(sa.Numeric(12, 2), nullable=True)
    house_type = sa.Column(sa.String, nullable=True)
    rent_amount = sa.Column(sa.Numeric(12, 2), nullable=True)
    family_income_data = sa.Column(postgresql.JSONB, nullable=True)
    financial_assistance_data = sa.Column(postgresql.JSONB, nullable=True)

    admission = relationship("Admission", back_populates="economic_situation")


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False)
    full_name = sa.Column(sa.String, nullable=False)

    admission = relationship("Admission", back_populates="household_members")


class ConsumptionSnapshot(Base):
    __tablename__ = "consumption_snapshots"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    age_first_use = sa.Column(sa.Integer, nullable=True)
    primary_drug = sa.Column(sa.String, nullable=True)
    drug_use_frequency = sa.Column(sa.String, nullable=True)
    other_drugs = sa.Column(postgresql.JSONB, nullable=True)
    previous_internments_count = sa.Column(sa.Integer, nullable=True)
    previous_internment_places = sa.Column(postgresql.JSONB, nullable=True)
    worst_experience = sa.Column(sa.Text, nullable=True)
    history_notes = sa.Column(sa.Text, nullable=True)

    admission = relationship("Admission", back_populates="consumption_snapshot")
