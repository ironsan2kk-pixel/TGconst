"""
Обработчики команд и сообщений бота
"""

from aiogram import Dispatcher, Router

from . import start
from . import menu
from . import channels
from . import tariffs
from . import payment

# Создаём главный роутер
router = Router()

# Подключаем все роутеры хендлеров
router.include_router(start.router)
router.include_router(menu.router)
router.include_router(channels.router)
router.include_router(tariffs.router)
router.include_router(payment.router)


def register_all_handlers(dp: Dispatcher) -> None:
    """
    Регистрация всех хендлеров в диспетчере.
    Совместимость с run.py
    """
    # Подключаем handlers роутер
    dp.include_router(router)
    
    # Подключаем callbacks роутер
    try:
        from ..callbacks import router as callbacks_router
        dp.include_router(callbacks_router)
    except ImportError:
        pass  # callbacks может быть не создан


__all__ = ["router", "register_all_handlers"]
