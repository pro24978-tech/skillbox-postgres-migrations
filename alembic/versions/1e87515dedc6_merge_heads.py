"""merge heads

Revision ID: 1e87515dedc6
Revises: 1abe5dc68386, 2df22a228c2c
Create Date: 2026-10-22 01:00:11.262995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e87515dedc6'
down_revision: Union[str, None] = ('1abe5dc68386', '2df22a228c2c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
