"""add shift handover tables

Revision ID: abad22e3de5b
Revises: 85f8f6035f08
Create Date: 2026-06-29 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'abad22e3de5b'
down_revision: Union[str, None] = '85f8f6035f08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# El enum 'shift' ya existe (creado por la migración de asistencia): no recrearlo.
shift_enum = postgresql.ENUM('morning', 'afternoon', 'night', name='shift', create_type=False)
handover_status = postgresql.ENUM('open', 'closed', 'received', name='handoverstatus', create_type=False)
incident_severity = postgresql.ENUM('low', 'medium', 'high', name='incidentseverity', create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    # Crear los enums nuevos (idempotente). El enum 'shift' se reutiliza.
    handover_status.create(bind, checkfirst=True)
    incident_severity.create(bind, checkfirst=True)

    op.create_table(
        'shift_handovers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('shift', shift_enum, nullable=False),
        sa.Column('auto_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('closed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('received_by_user_id', sa.Integer(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', handover_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['closed_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['received_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', 'shift', name='uq_shift_handover_date_shift'),
    )
    op.create_index(op.f('ix_shift_handovers_id'), 'shift_handovers', ['id'], unique=False)

    op.create_table(
        'shift_incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('handover_id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('severity', incident_severity, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('action_taken', sa.Text(), nullable=True),
        sa.Column('reported_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admissions.id'], ),
        sa.ForeignKeyConstraint(['handover_id'], ['shift_handovers.id'], ),
        sa.ForeignKeyConstraint(['reported_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_shift_incidents_id'), 'shift_incidents', ['id'], unique=False)

    op.create_table(
        'shift_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('handover_id', sa.Integer(), nullable=False),
        sa.Column('related_admission_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_done', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('done_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['done_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['handover_id'], ['shift_handovers.id'], ),
        sa.ForeignKeyConstraint(['related_admission_id'], ['admissions.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_shift_tasks_id'), 'shift_tasks', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_shift_tasks_id'), table_name='shift_tasks')
    op.drop_table('shift_tasks')
    op.drop_index(op.f('ix_shift_incidents_id'), table_name='shift_incidents')
    op.drop_table('shift_incidents')
    op.drop_index(op.f('ix_shift_handovers_id'), table_name='shift_handovers')
    op.drop_table('shift_handovers')
    incident_severity.drop(op.get_bind(), checkfirst=True)
    handover_status.drop(op.get_bind(), checkfirst=True)
