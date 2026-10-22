"""add patronymic

Revision ID: 1abe5dc68386
Revises: 2df22a228c2c
Create Date: 2026-10-22 00:55:27.025741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1abe5dc68386'
down_revision: Union[str, None] = 'c495e06d1d27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('patronymic', sa.String(length=50), nullable=True))
    


def downgrade() -> None:
    op.drop_column('users', 'patronymic')
