"""
Обработчики команд и сообщений бота
"""

from aiogram import Router

from . import start
from . import menu
from . import channels
from . import tariffs
from . import payment

router = Router()

# Подключаем все роутеры
router.include_router(start.router)
router.include_router(menu.router)
router.include_router(channels.router)
router.include_router(tariffs.router)
router.include_router(payment.router)

__all__ = ["router"]
