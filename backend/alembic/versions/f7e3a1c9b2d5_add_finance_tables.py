"""add finance tables

Revision ID: f7e3a1c9b2d5
Revises: abad22e3de5b
Create Date: 2026-06-29 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f7e3a1c9b2d5'
down_revision: Union[str, None] = 'abad22e3de5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

agreement_type = postgresql.ENUM(
    'monthly', 'fixed_total', 'scholarship_full', 'scholarship_partial',
    name='agreementtype', create_type=False,
)
payment_method = postgresql.ENUM(
    'cash', 'sinpe', 'transfer', 'check', 'other',
    name='paymentmethod', create_type=False,
)
payer_type = postgresql.ENUM(
    'family', 'iafa', 'imas', 'church', 'donor', 'other',
    name='payertype', create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    agreement_type.create(bind, checkfirst=True)
    payment_method.create(bind, checkfirst=True)
    payer_type.create(bind, checkfirst=True)

    op.create_table(
        'payment_agreements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('agreement_type', agreement_type, nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('billing_day', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admissions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admission_id', name='uq_payment_agreements_admission'),
    )
    op.create_index(op.f('ix_payment_agreements_id'), 'payment_agreements', ['id'], unique=False)

    op.create_table(
        'charges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('concept', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('charge_date', sa.Date(), nullable=False),
        sa.Column('period', sa.String(7), nullable=True),
        sa.Column('is_auto', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admissions.id']),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_charges_id'), 'charges', ['id'], unique=False)
    # Partial unique index: prevents duplicate monthly period per admission;
    # rows with period=NULL (manual charges) are excluded and never conflict.
    op.create_index(
        'uq_charges_admission_period',
        'charges',
        ['admission_id', 'period'],
        unique=True,
        postgresql_where=sa.text('period IS NOT NULL'),
    )

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admission_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('method', payment_method, nullable=False),
        sa.Column('payer_type', payer_type, nullable=False),
        sa.Column('payer_name', sa.String(), nullable=True),
        sa.Column('reference', sa.String(), nullable=True),
        sa.Column('receipt_number', sa.Integer(), nullable=False),
        sa.Column('received_by_user_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admission_id'], ['admissions.id']),
        sa.ForeignKeyConstraint(['received_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('receipt_number', name='uq_payments_receipt_number'),
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index('uq_charges_admission_period', table_name='charges')
    op.drop_index(op.f('ix_charges_id'), table_name='charges')
    op.drop_table('charges')
    op.drop_index(op.f('ix_payment_agreements_id'), table_name='payment_agreements')
    op.drop_table('payment_agreements')
    payer_type.drop(op.get_bind(), checkfirst=True)
    payment_method.drop(op.get_bind(), checkfirst=True)
    agreement_type.drop(op.get_bind(), checkfirst=True)
