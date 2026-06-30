"""
Modelos para el módulo de Ocupación + Lista de espera.

Tablas:
  - clinic_settings: clave-valor para settings del centro (ej. capacity).
  - waitlist_entries: lista de espera para admisión.
"""

import enum
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class WaitlistStatus(str, enum.Enum):
    waiting = "waiting"
    admitted = "admitted"
    declined = "declined"
    cancelled = "cancelled"


class ClinicSetting(Base):
    """
    Tabla key-value para settings del centro.
    Actualmente se usa la clave 'capacity' (int almacenado como str).
    Reutilizable para futuros settings globales.
    """
    __tablename__ = "clinic_settings"

    key = sa.Column(sa.String, primary_key=True)
    value = sa.Column(sa.String, nullable=False)


class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    full_name = sa.Column(sa.String, nullable=False)
    contact_phone = sa.Column(sa.String, nullable=True)
    contact_email = sa.Column(sa.String, nullable=True)
    requested_at = sa.Column(sa.Date, nullable=False, server_default=sa.func.current_date())
    referred_by = sa.Column(sa.String, nullable=True)
    status = sa.Column(
        sa.Enum(WaitlistStatus),
        nullable=False,
        default=WaitlistStatus.waiting,
        server_default=WaitlistStatus.waiting.value,
    )
    notes = sa.Column(sa.Text, nullable=True)
    created_by_user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    created_by = relationship("User", foreign_keys=[created_by_user_id])
