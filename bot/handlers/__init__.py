"""
Хендлеры бота.
"""

from aiogram import Router

from bot.handlers import start, menu, language, tariffs


def setup_handlers() -> Router:
    """Настроить и вернуть роутер со всеми хендлерами."""
    router = Router()
    
    # Подключаем роутеры
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(language.router)
    router.include_router(tariffs.router)
    
    return router
