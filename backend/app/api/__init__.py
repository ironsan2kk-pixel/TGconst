"""
API роутеры
"""
from fastapi import APIRouter

from .auth import router as auth_router

# Главный роутер API
api_router = APIRouter(prefix="/api")

# Подключаем роутеры
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
