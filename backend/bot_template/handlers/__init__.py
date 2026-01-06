"""
Обработчики команд и сообщений бота
"""

from aiogram import Dispatcher, Router

from . import start
from . import menu
from . import channels
from . import tariffs
from . import payment
from . import promocode
from . import subscription
from . import support

# Создаём главный роутер
router = Router()

# Подключаем все роутеры хендлеров
# Порядок важен: более специфичные роутеры должны быть выше
router.include_router(start.router)
router.include_router(promocode.router)      # Промокоды (Этап 12)
router.include_router(subscription.router)   # Подписки (Этап 12)
router.include_router(support.router)        # Поддержка (Этап 12)
router.include_router(menu.router)           # Главное меню
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
