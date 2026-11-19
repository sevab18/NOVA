from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.products.schemas import ProductCreate, ProductResponse
from app.products.service import ProductService
from app.users.dependencies import require_admin
from app.users.models import User

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products(db: Session=Depends(get_db)):
     service = ProductService(db)

     return service.get_products()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    return ProductService(db).get_product(product_id)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    service = ProductService(db)

    return service.create_product(data)
