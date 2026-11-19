from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.category.models import Category
from app.products.models import Product
from app.products.repository import ProductRepository
from app.products.schemas import (
    ProductCreate,
    ProductListResponse,
    ProductSort,
    ProductUpdate,
)


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepository(db)

    def get_products(
        self,
        *,
        query: str | None,
        category_id: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        sort: ProductSort,
        page: int,
        page_size: int,
    ) -> ProductListResponse:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="min_price cannot be greater than max_price",
            )

        normalized_query = query.strip() if query else None
        items, total = self.repository.get_page(
            query=normalized_query or None,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            page=page,
            page_size=page_size,
        )
        pages = (total + page_size - 1) // page_size
        return ProductListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def get_product(self, product_id: int) -> Product:
        product = self.repository.get_by_id(product_id)
        if product is None or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product

    def create_product(self, data: ProductCreate) -> Product:
        self._validate_category(data.category_id)

        try:
            product = self.repository.create(
                name=data.name,
                description=data.description,
                price=data.price,
                stock=data.stock,
                category_id=data.category_id,
                image_url=data.image_url,
                is_active=data.is_active,
            )
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception:
            self.db.rollback()
            raise

    def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        changes = data.model_dump(exclude_unset=True)
        required_fields = {"name", "price", "stock", "is_active"}
        invalid_null_fields = sorted(
            field
            for field in required_fields
            if field in changes and changes[field] is None
        )
        if invalid_null_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Fields cannot be null: {', '.join(invalid_null_fields)}",
            )

        if "category_id" in changes:
            self._validate_category(changes["category_id"])

        try:
            self.repository.update(product, changes)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception:
            self.db.rollback()
            raise

    def _validate_category(self, category_id: int | None) -> None:
        if category_id is None:
            return
        if self.db.get(Category, category_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
