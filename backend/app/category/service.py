from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.category.models import Category
from app.category.repository import CategoryRepository
from app.category.schemas import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self,db:Session):
        self.db=db
        self.repository=CategoryRepository(db)


    def get_categories(self) -> list[Category]:
        return self.repository.get_all()

    def get_category(self, category_id: int) -> Category:
        category = self.repository.get_by_id(category_id)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        return category

    def create_category(self, data: CategoryCreate) -> Category:
        try:
            category = self.repository.create(
                name=data.name,
                description=data.description
            )

            self.db.commit()
            self.db.refresh(category)

            return category

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Category name already exists"
            )

        except Exception:
            self.db.rollback()
            raise

    def update_category(
        self,
        category_id: int,
        data: CategoryUpdate
    ) -> Category:
        category = self.get_category(category_id)

        changes = data.model_dump(exclude_unset=True)

        if "name" in changes and changes["name"] is None:
            raise HTTPException(
                status_code=422,
                detail="Category name cannot be null"
            )

        for field, value in changes.items():
            setattr(category, field, value)

        try:
            self.db.commit()
            self.db.refresh(category)

            return category

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Category update violates a database constraint"
            )

        except Exception:
            self.db.rollback()
            raise

    def delete_category(self, category_id: int) -> None:
        category = self.get_category(category_id)

        try:
            self.repository.delete(category)
            self.db.commit()

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Category cannot be deleted because it is referenced"
            )

        except Exception:
            self.db.rollback()
            raise
