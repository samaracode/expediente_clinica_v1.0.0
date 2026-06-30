import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    admission_id = sa.Column(sa.Integer, sa.ForeignKey("admissions.id"), nullable=False, unique=True)
    social_security_validated = sa.Column(sa.Boolean, default=False)
    iafa_icd_data = sa.Column(postgresql.JSONB, nullable=True)
    completion_status = sa.Column(sa.String, default="pending")

    admission = relationship("Admission", back_populates="medical_record")
    drug_tests = relationship("DrugTest", back_populates="medical_record")
    medication_logs = relationship("MedicationLog", back_populates="medical_record")


class DrugTest(Base):
    __tablename__ = "drug_tests"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    medical_record_id = sa.Column(sa.Integer, sa.ForeignKey("medical_records.id"), nullable=False)
    test_date = sa.Column(sa.Date, nullable=False)
    result = sa.Column(sa.String, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)
    file_id = sa.Column(sa.Integer, sa.ForeignKey("files.id"), nullable=True)

    medical_record = relationship("MedicalRecord", back_populates="drug_tests")


class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    medical_record_id = sa.Column(sa.Integer, sa.ForeignKey("medical_records.id"), nullable=False)
    treatment_type = sa.Column(sa.String, nullable=True)
    medication_name = sa.Column(sa.String, nullable=False)
    dosage = sa.Column(sa.String, nullable=True)
    frequency = sa.Column(sa.String, nullable=True)
    prescribed_by = sa.Column(sa.String, nullable=True)
    start_date = sa.Column(sa.Date, nullable=True)
    end_date = sa.Column(sa.Date, nullable=True)
    notes = sa.Column(sa.Text, nullable=True)

    medical_record = relationship("MedicalRecord", back_populates="medication_logs")
