"""
Инициализация бота и диспетчера Aiogram 3.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import config


# Создаём бота
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True,
    )
)

# Создаём диспетчер
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
