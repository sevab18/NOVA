##работа с PostgreSQL

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.products.models import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db=db

    def get_all(self)-> list[Product]:
        stmt=select(Product).order_by(Product.id)


        return list(self.db.scalars(stmt).all())

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def create (
            self,
            name: str,
            description: str | None,
            price,
            stock: int,
            category_id: int | None,
    )-> Product:
        product=Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )

        self.db.add(product)
        self.db.flush()

        return product

    
