from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.category.router import router as categories_router
from app.products.router import router as products_router
from app.users.router import router as users_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
api_router.include_router(categories_router)
