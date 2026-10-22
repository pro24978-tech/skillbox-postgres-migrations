"""remove has_sale

Revision ID: c495e06d1d27
Revises: abd588cf8f81
Create Date: 2026-10-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c495e06d1d27'
down_revision = 'abd588cf8f81'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('users', 'has_sale')


def downgrade() -> None:
    op.add_column('users', sa.Column('has_sale', sa.Boolean(), nullable=True))
