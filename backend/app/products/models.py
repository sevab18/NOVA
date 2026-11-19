from decimal import Decimal 
from sqlalchemy import CheckConstraint, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship



from app.database import Base 

class Product(Base):
    __tablename__="products"

    id: Mapped[int]= mapped_column(primary_key=True)

    name: Mapped[str]=mapped_column(
        String(200),
        nullable=False

    )

    description: Mapped[str | None]=mapped_column(
        String(1000),
        nullable=True
    )

    price: Mapped[Decimal]=mapped_column (
        Numeric(12,2),
        nullable=False
    )

    stock: Mapped[int]=mapped_column(
        nullable=False,
        default=0
    )

    __table_args__=(
        CheckConstraint("price >= 0", name="ck_products_price"),
        CheckConstraint("stock>=0",name="ck_products_stock" )
    )

    category_id: Mapped[int | None] = mapped_column(
    ForeignKey("categories.id", ondelete="RESTRICT"),
    nullable=True
)

    category: Mapped["Category | None"] = relationship(
    "Category",
    back_populates="products"
)

