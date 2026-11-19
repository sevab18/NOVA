from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Category(Base):
    __tablename__="categories"

    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(
        String(100),
        nullable=False,
        unique=True
    )
    description: Mapped[str | None]=mapped_column(
        String(500),
        nullable=True
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category"
    )
