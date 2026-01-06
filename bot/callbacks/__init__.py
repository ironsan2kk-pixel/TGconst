"""
Callback-обработчики бота.
"""

from aiogram import Router

from bot.callbacks import language, tariff, payment


def setup_callbacks() -> Router:
    """Настроить и вернуть роутер с callback-обработчиками."""
    router = Router()
    
    router.include_router(language.router)
    router.include_router(tariff.router)
    router.include_router(payment.router)
    
    return router
