"""
Регистрация всех хендлеров бота
"""
from aiogram import Dispatcher

from .start import router as start_router
from .menu import router as menu_router
from .channels import router as channels_router
from .tariffs import router as tariffs_router


def register_all_handlers(dp: Dispatcher):
    """
    Регистрация всех роутеров в диспетчере.
    
    Args:
        dp: Диспетчер aiogram
    """
    # Порядок важен! Более специфичные хендлеры идут раньше
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(channels_router)
    dp.include_router(tariffs_router)
