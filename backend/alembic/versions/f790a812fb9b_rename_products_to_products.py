"""rename Products to products

Revision ID: f790a812fb9b
Revises: f97f95adc06f
Create Date: 2026-10-27 16:30:21.566294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f790a812fb9b'
down_revision: Union[str, Sequence[str], None] = 'f97f95adc06f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Переименовать Products в products."""
    op.rename_table("Products", "products")


def downgrade() -> None:
    """Вернуть прежнее название таблицы."""
    op.rename_table("products", "Products")