from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.products.models import Product
from app.products.schemas import ProductSort


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_page(
        self,
        *,
        query: str | None,
        category_id: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        sort: ProductSort,
        page: int,
        page_size: int,
    ) -> tuple[list[Product], int]:
        filters = [Product.is_active.is_(True)]

        if query:
            search_pattern = f"%{query}%"
            filters.append(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                )
            )
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if min_price is not None:
            filters.append(Product.price >= min_price)
        if max_price is not None:
            filters.append(Product.price <= max_price)

        total_stmt = select(func.count()).select_from(Product).where(*filters)
        total = self.db.scalar(total_stmt) or 0

        order_by = {
            ProductSort.NEWEST: (Product.id.desc(),),
            ProductSort.PRICE_ASC: (Product.price.asc(), Product.id.asc()),
            ProductSort.PRICE_DESC: (Product.price.desc(), Product.id.desc()),
            ProductSort.NAME_ASC: (Product.name.asc(), Product.id.asc()),
            ProductSort.NAME_DESC: (Product.name.desc(), Product.id.desc()),
        }[sort]

        stmt = (
            select(Product)
            .where(*filters)
            .order_by(*order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def create(
        self,
        *,
        name: str,
        description: str | None,
        price: Decimal,
        stock: int,
        category_id: int | None,
        image_url: str | None,
        is_active: bool,
    ) -> Product:
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            image_url=image_url,
            is_active=is_active,
        )
        self.db.add(product)
        self.db.flush()
        return product

    def update(self, product: Product, changes: dict) -> Product:
        for field, value in changes.items():
            setattr(product, field, value)
        self.db.flush()
        return product
