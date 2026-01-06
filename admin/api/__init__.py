"""
Admin API - Main Router
Регистрация всех API endpoints
"""

from fastapi import APIRouter

from .dashboard import router as dashboard_router
from .channels import router as channels_router
from .tariffs import router as tariffs_router
from .users import router as users_router
from .subscriptions import router as subscriptions_router
from .payments import router as payments_router
from .promocodes import router as promocodes_router
from .menu import router as menu_router
from .faq import router as faq_router
from .settings import router as settings_router
from .export import router as export_router
from .backup import router as backup_router

# Главный роутер API
api_router = APIRouter(prefix="/api")

# Регистрация всех роутеров
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(channels_router, prefix="/channels", tags=["Channels"])
api_router.include_router(tariffs_router, prefix="/tariffs", tags=["Tariffs"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(subscriptions_router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(promocodes_router, prefix="/promocodes", tags=["Promocodes"])
api_router.include_router(menu_router, prefix="/menu", tags=["Menu Builder"])
api_router.include_router(faq_router, prefix="/faq", tags=["FAQ"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(export_router, prefix="/export", tags=["Export"])
api_router.include_router(backup_router, prefix="/backup", tags=["Backup"])

__all__ = ["api_router"]
