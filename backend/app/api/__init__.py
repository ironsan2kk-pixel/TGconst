"""
API роутеры
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .bots import router as bots_router
from .channels import router as channels_router
from .tariffs import router as tariffs_router
from .promocodes import router as promocodes_router

# Главный роутер API
api_router = APIRouter(prefix="/api")

# Подключаем роутеры
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(bots_router, prefix="/bots", tags=["Bots"])

# Роутеры для работы с данными бота (каналы, тарифы, промокоды)
# Префикс /bots/{bot_uuid} — все операции в контексте конкретного бота
api_router.include_router(
    channels_router, 
    prefix="/bots/{bot_uuid}/channels", 
    tags=["Channels"]
)
api_router.include_router(
    tariffs_router, 
    prefix="/bots/{bot_uuid}", 
    tags=["Tariffs"]
)
api_router.include_router(
    promocodes_router, 
    prefix="/bots/{bot_uuid}/promocodes", 
    tags=["Promocodes"]
)
