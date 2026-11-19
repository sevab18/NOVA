from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.category.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from app.category.service import CategoryService
from app.users.dependencies import require_admin
from app.users.models import User


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    "",
    response_model=list[CategoryResponse]
)
def get_categories(db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.get_categories()


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    service = CategoryService(db)
    return service.get_category(category_id)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    service = CategoryService(db)
    return service.create_category(data)


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    service = CategoryService(db)
    return service.update_category(category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    service = CategoryService(db)
    service.delete_category(category_id)
