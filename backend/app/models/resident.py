import enum
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Sex(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class MaritalStatus(str, enum.Enum):
    single = "single"
    married = "married"
    divorced = "divorced"
    widowed = "widowed"
    common_law = "common_law"


class EducationLevel(str, enum.Enum):
    none = "none"
    primary = "primary"
    secondary = "secondary"
    technical = "technical"
    university = "university"
    postgraduate = "postgraduate"


class Resident(Base):
    __tablename__ = "residents"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    code = sa.Column(sa.String, unique=True, nullable=False, index=True)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    id_number = sa.Column(sa.String, unique=True, nullable=True, index=True)
    birthdate = sa.Column(sa.Date, nullable=True)
    sex = sa.Column(sa.Enum(Sex), nullable=True)
    marital_status = sa.Column(sa.Enum(MaritalStatus), nullable=True)
    nationality = sa.Column(sa.String, nullable=True)
    province = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String, nullable=True)
    district = sa.Column(sa.String, nullable=True)
    neighborhood = sa.Column(sa.String, nullable=True)
    address_other = sa.Column(sa.String, nullable=True)
    phone_home = sa.Column(sa.String, nullable=True)
    phone_mobile = sa.Column(sa.String, nullable=True)
    emergency_contact_name = sa.Column(sa.String, nullable=True)
    emergency_contact_phone = sa.Column(sa.String, nullable=True)
    is_insured = sa.Column(sa.Boolean, default=False)
    insurance_type = sa.Column(sa.String, nullable=True)
    photo_file_id = sa.Column(sa.Integer, sa.ForeignKey("files.id"), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    admissions = relationship("Admission", back_populates="resident")
    family_members = relationship("FamilyMember", back_populates="resident")
    education_records = relationship("EducationRecord", back_populates="resident")
    patient_relatives = relationship("PatientRelative", back_populates="resident")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    resident_id = sa.Column(sa.Integer, sa.ForeignKey("residents.id"), nullable=False)
    full_name = sa.Column(sa.String, nullable=False)
    relation_type = sa.Column(sa.String, nullable=True)
    age = sa.Column(sa.Integer, nullable=True)

    resident = relationship("Resident", back_populates="family_members")


class EducationRecord(Base):
    __tablename__ = "education_records"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    resident_id = sa.Column(sa.Integer, sa.ForeignKey("residents.id"), nullable=False)
    level = sa.Column(sa.String, nullable=True)
    academic_grade = sa.Column(sa.String, nullable=True)
    year_attended = sa.Column(sa.Integer, nullable=True)
    institution_name = sa.Column(sa.String, nullable=True)

    resident = relationship("Resident", back_populates="education_records")


class Relative(Base):
    __tablename__ = "relatives"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    id_number = sa.Column(sa.String, unique=True, nullable=True, index=True)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    birthdate = sa.Column(sa.Date, nullable=True)
    marital_status = sa.Column(sa.Enum(MaritalStatus), nullable=True)
    address = sa.Column(sa.String, nullable=True)
    judicial_situation = sa.Column(sa.String, nullable=True)
    phone = sa.Column(sa.String, nullable=True)
    education_level = sa.Column(sa.Enum(EducationLevel), nullable=True)

    patient_relatives = relationship("PatientRelative", back_populates="relative")


class PatientRelative(Base):
    __tablename__ = "patient_relatives"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    resident_id = sa.Column(sa.Integer, sa.ForeignKey("residents.id"), nullable=False)
    relative_id = sa.Column(sa.Integer, sa.ForeignKey("relatives.id"), nullable=False)
    relation_type = sa.Column(sa.String, nullable=False)

    resident = relationship("Resident", back_populates="patient_relatives")
    relative = relationship("Relative", back_populates="patient_relatives")
