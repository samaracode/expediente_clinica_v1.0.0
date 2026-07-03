"""add user module permissions (ADR 0003: authorization by-user, not by-role)

Revision ID: a1b2c3d4e5f6
Revises: f7e3a1c9b2d5
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f7e3a1c9b2d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

module_enum = postgresql.ENUM(
    'residents', 'operations', 'finance', 'reports',
    'medical', 'psychology', 'therapeutic', 'social_work', 'occupational_therapy',
    name='module', create_type=False,
)

# Mapeo hardcoded que reemplazamos (access.ts + RoleRequired por router),
# usado para backfill: cada usuario existente conserva los módulos que ya
# podía usar por su rol, para no perder acceso al migrar.
ROLE_TO_MODULES = {
    'admin': [],  # admin tiene acceso total implícito, no necesita filas
    'receptionist': ['finance'],
    'medical': ['medical'],
    'counselor': ['medical', 'therapeutic'],
    'social_worker': ['social_work'],
    'psychologist': ['psychology'],
    'occupational_therapist': ['occupational_therapy'],
}
# Módulos sin restricción hoy (cualquier usuario autenticado entra):
# residents, operations, reports. Se conceden a todos los no-admin en el
# backfill para no quitarle acceso a nadie.
OPEN_MODULES = ['residents', 'operations', 'reports']


def upgrade() -> None:
    bind = op.get_bind()
    module_enum.create(bind, checkfirst=True)

    op.create_table(
        'user_module_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('module', module_enum, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'module', name='uq_user_module_permissions_user_module'),
    )
    op.create_index(
        op.f('ix_user_module_permissions_id'), 'user_module_permissions', ['id'], unique=False
    )

    # Backfill: derivar permisos desde el rol actual de cada usuario para
    # preservar exactamente los accesos que ya tenían (ver ADR 0003).
    conn = op.get_bind()
    users = conn.execute(sa.text("SELECT id, role FROM users")).fetchall()
    rows = []
    for user_id, role in users:
        if role == 'admin':
            continue  # admin no necesita filas: acceso total implícito
        modules = set(ROLE_TO_MODULES.get(role, [])) | set(OPEN_MODULES)
        for module in modules:
            rows.append({"user_id": user_id, "module": module})
    if rows:
        op.bulk_insert(
            sa.table(
                'user_module_permissions',
                sa.column('user_id', sa.Integer),
                sa.column('module', module_enum),
            ),
            rows,
        )


def downgrade() -> None:
    op.drop_index(op.f('ix_user_module_permissions_id'), table_name='user_module_permissions')
    op.drop_table('user_module_permissions')
    module_enum.drop(op.get_bind(), checkfirst=True)
