"""
Хендлеры бота.
"""

from aiogram import Router

from bot.handlers import (
    start,
    menu_navigation,  # ВАЖНО: должен быть ПЕРЕД menu!
    menu,
    language,
    tariffs,
    payment,
    promocode,
    subscription,
    faq,
    admin,
)


def setup_handlers() -> Router:
    """Настроить и вернуть роутер со всеми хендлерами."""
    router = Router()
    
    # Подключаем роутеры
    # ПОРЯДОК ВАЖЕН! menu_navigation перед menu для приоритета динамического меню
    router.include_router(start.router)
    router.include_router(menu_navigation.router)  # Динамическое меню из БД
    router.include_router(menu.router)             # Статические пункты меню
    router.include_router(language.router)
    router.include_router(tariffs.router)
    router.include_router(payment.router)
    router.include_router(promocode.router)
    router.include_router(subscription.router)
    router.include_router(faq.router)
    router.include_router(admin.router)
    
    return router

