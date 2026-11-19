"""fix products table name

Revision ID: 2964d08fe7cc
Revises: f790a812fb9b
Create Date: 2026-11-03 12:15:36.048367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2964d08fe7cc'
down_revision: Union[str, Sequence[str], None] = 'f790a812fb9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
