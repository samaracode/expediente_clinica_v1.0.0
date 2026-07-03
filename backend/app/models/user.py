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


class Module(str, enum.Enum):
    """Módulos configurables de acceso por usuario (ADR 0003).

    `admin` no tiene módulo propio: el rol admin tiene acceso total implícito.
    `dashboard` tampoco es configurable: siempre visible para cualquier usuario.
    """
    residents = "residents"
    operations = "operations"
    finance = "finance"
    reports = "reports"
    medical = "medical"
    psychology = "psychology"
    therapeutic = "therapeutic"
    social_work = "social_work"
    occupational_therapy = "occupational_therapy"


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
    module_permissions = relationship(
        "UserModulePermission", back_populates="user", cascade="all, delete-orphan"
    )

    def allowed_modules(self) -> set:
        """Módulos habilitados. admin implícitamente tiene todos."""
        if self.role == UserRole.admin:
            return set(Module)
        return {p.module for p in self.module_permissions}

    def has_module(self, module: "Module") -> bool:
        if self.role == UserRole.admin:
            return True
        return any(p.module == module for p in self.module_permissions)


class UserModulePermission(Base):
    __tablename__ = "user_module_permissions"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "module", name="uq_user_module_permissions_user_module"),
    )

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    module = sa.Column(sa.Enum(Module), nullable=False)

    user = relationship("User", back_populates="module_permissions")


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
