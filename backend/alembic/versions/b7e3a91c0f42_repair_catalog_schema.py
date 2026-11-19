"""repair catalog schema

Revision ID: b7e3a91c0f42
Revises: 2964d08fe7cc
Create Date: 2026-11-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7e3a91c0f42"
down_revision: Union[str, Sequence[str], None] = "2964d08fe7cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    table_names = set(sa.inspect(bind).get_table_names())

    if "Products" in table_names and "products" in table_names:
        raise RuntimeError(
            'Both "Products" and "products" tables exist; '
            "manual data reconciliation is required."
        )

    if "Products" in table_names:
        op.rename_table("Products", "products")

    table_names = set(sa.inspect(bind).get_table_names())
    if "categories" not in table_names:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=500), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )

    product_columns = {
        column["name"]
        for column in sa.inspect(bind).get_columns("products")
    }
    if "category_id" not in product_columns:
        op.add_column(
            "products",
            sa.Column("category_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_products_category_id_categories",
            "products",
            "categories",
            ["category_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    bind = op.get_bind()
    table_names = set(sa.inspect(bind).get_table_names())

    if "products" in table_names:
        product_columns = {
            column["name"]
            for column in sa.inspect(bind).get_columns("products")
        }
        if "category_id" in product_columns:
            op.drop_constraint(
                "fk_products_category_id_categories",
                "products",
                type_="foreignkey",
            )
            op.drop_column("products", "category_id")

    if "categories" in table_names:
        op.drop_table("categories")

    table_names = set(sa.inspect(bind).get_table_names())
    if "products" in table_names and "Products" not in table_names:
        op.rename_table("products", "Products")
