"""extend product catalog

Revision ID: 8f4c2a1d9b70
Revises: c4a19d6f28b1
Create Date: 2026-11-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f4c2a1d9b70"
down_revision: Union[str, Sequence[str], None] = "c4a19d6f28b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("image_url", sa.String(length=2048), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "is_active")
    op.drop_column("products", "image_url")
