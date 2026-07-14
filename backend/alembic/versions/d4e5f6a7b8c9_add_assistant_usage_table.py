"""add assistant_usage table (tope de gasto mensual del asistente "Ask AI")

Revision ID: d4e5f6a7b8c9
Revises: a1b2c3d4e5f6
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'assistant_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('total_cost_usd', sa.Numeric(precision=12, scale=6), nullable=False, server_default='0'),
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period', name='uq_assistant_usage_period'),
    )
    op.create_index(op.f('ix_assistant_usage_id'), 'assistant_usage', ['id'], unique=False)
    op.create_index(op.f('ix_assistant_usage_period'), 'assistant_usage', ['period'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assistant_usage_period'), table_name='assistant_usage')
    op.drop_index(op.f('ix_assistant_usage_id'), table_name='assistant_usage')
    op.drop_table('assistant_usage')
