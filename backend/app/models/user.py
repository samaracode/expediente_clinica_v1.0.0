import enum
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    counselor = "counselor"
    medical = "medical"
    social_worker = "social_worker"
    psychologist = "psychologist"
    occupational_therapist = "occupational_therapist"
    receptionist = "receptionist"


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    full_name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, unique=True, index=True, nullable=False)
    hashed_password = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.Enum(UserRole), nullable=False, default=UserRole.counselor)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    professional = relationship("Professional", back_populates="user", uselist=False)


class TreatmentArea(Base):
    __tablename__ = "treatment_areas"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, nullable=False)
    description = sa.Column(sa.String, nullable=True)

    professionals = relationship("Professional", back_populates="area")


class Professional(Base):
    __tablename__ = "professionals"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    area_id = sa.Column(sa.Integer, sa.ForeignKey("treatment_areas.id"), nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    specialty = sa.Column(sa.String, nullable=True)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="professional")
    area = relationship("TreatmentArea", back_populates="professionals")
