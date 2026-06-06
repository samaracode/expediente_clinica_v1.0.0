import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class TherapeuticAssessment(Base):
    __tablename__ = "therapeutic_assessments"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    assessor_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    assessment_date = sa.Column(sa.Date, nullable=True)
    initial_summary = sa.Column(sa.Text, nullable=True)
    clinical_history_summary = sa.Column(sa.Text, nullable=True)
    europal_si_data = sa.Column(postgresql.JSONB, nullable=True)
    socrates_data = sa.Column(postgresql.JSONB, nullable=True)
    urica_data = sa.Column(postgresql.JSONB, nullable=True)
    afc_analysis = sa.Column(postgresql.JSONB, nullable=True)
    relapse_prevention_interview = sa.Column(sa.Text, nullable=True)
    relapse_prevention_plan = sa.Column(sa.Text, nullable=True)
    completion_status = sa.Column(sa.String, default="pending")

    admission = relationship("Admission", back_populates="therapeutic_assessment")
    assessor = relationship("User", foreign_keys=[assessor_id])


class SocialWorkAssessment(Base):
    __tablename__ = "social_work_assessments"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    social_worker_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    assessment_date = sa.Column(sa.Date, nullable=True)
    diagnostic_impression = sa.Column(sa.Text, nullable=True)
    initial_assessment = sa.Column(sa.Text, nullable=True)
    completion_status = sa.Column(sa.String, default="pending")

    admission = relationship("Admission", back_populates="social_work_assessment")
    social_worker = relationship("User", foreign_keys=[social_worker_id])


class PsychologyAssessment(Base):
    __tablename__ = "psychology_assessments"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    psychologist_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    assessment_date = sa.Column(sa.Date, nullable=True)
    initial_diagnostic_impression = sa.Column(sa.Text, nullable=True)
    observable_assessment = sa.Column(sa.Text, nullable=True)
    diagnostic_tests = sa.Column(postgresql.JSONB, nullable=True)
    completion_status = sa.Column(sa.String, default="pending")

    admission = relationship("Admission", back_populates="psychology_assessment")
    psychologist = relationship("User", foreign_keys=[psychologist_id])


class OccupationalTherapyAssessment(Base):
    __tablename__ = "occupational_therapy_assessments"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    therapist_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    assessment_date = sa.Column(sa.Date, nullable=True)
    initial_diagnostic_impression = sa.Column(sa.Text, nullable=True)
    occupational_profile = sa.Column(sa.Text, nullable=True)
    completion_status = sa.Column(sa.String, default="pending")

    admission = relationship("Admission", back_populates="occupational_therapy_assessment")
    therapist = relationship("User", foreign_keys=[therapist_id])
