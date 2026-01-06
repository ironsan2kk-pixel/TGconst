"""
Хендлеры бота.
"""

from aiogram import Router

from bot.handlers import (
    start,
    menu,
    language,
    tariffs,
    payment,
    promocode,
    subscription,
    menu_navigation,
    faq,
    admin,
)


def setup_handlers() -> Router:
    """Настроить и вернуть роутер со всеми хендлерами."""
    router = Router()
    
    # Подключаем роутеры
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(language.router)
    router.include_router(tariffs.router)
    router.include_router(payment.router)
    router.include_router(promocode.router)
    router.include_router(subscription.router)
    router.include_router(menu_navigation.router)
    router.include_router(faq.router)
    router.include_router(admin.router)
    
    return router
