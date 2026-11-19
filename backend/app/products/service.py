from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.category.models import Category
from app.products.repository import ProductRepository
from app.products.schemas import ProductCreate

class ProductService:
    def __init__(self, db: Session):
        self.db=db
        self.repository=ProductRepository(db)


    def get_products(self):
        return self.repository.get_all()

    def get_product(self, product_id: int):
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product

    def create_product(self, data:ProductCreate):
        try:
            if data.category_id is not None:
                category = self.db.get(Category, data.category_id)
                if category is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Category not found",
                    )

            product=self.repository.create(
                name=data.name,
                description=data.description,
                price=data.price,
                stock=data.stock,
                category_id=data.category_id,
            )
            self.db.commit()
            self.db.refresh(product)

            return product 
        except Exception:
            self.db.rollback()
            raise

            
