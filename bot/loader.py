"""
Инициализация бота и диспетчера Aiogram 3.
"""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import config

# Совместимость с разными версиями Aiogram 3.x
try:
    from aiogram.client.default import DefaultBotProperties
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
        )
    )
except ImportError:
    # Для старых версий Aiogram 3.x
    bot = Bot(
        token=config.BOT_TOKEN,
        parse_mode=ParseMode.HTML,
    )

# Создаём диспетчер
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
