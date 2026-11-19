from sqlalchemy import select
from sqlalchemy.orm import Session

from app.category.models import Category


class CategoryRepository:
    def __init__(self,db: Session):
        self.db=db

    def get_all(self)->list[Category]:
        stmt=select(Category).order_by(Category.id)

        return list(self.db.scalars(stmt).all())

    def get_by_id(self,category_id: int)-> Category | None:
        return self.db.get(Category, category_id)

    def create(
            self,
            name: str,
            description: str | None

    )->Category:
        category=Category(
            name=name,
            description=description
        )

        self.db.add(category)
        self.db.flush()

        return category

    def delete(self,category: Category)-> None:
        self.db.delete(category)
    


