"""
Точка входа Telegram бота.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot
from aiogram.types import BotCommand

from bot.config import config
from bot.loader import bot, dp
from bot.database import init_db
from bot.handlers import setup_handlers
from bot.callbacks import setup_callbacks
from bot.middlewares import (
    DatabaseMiddleware,
    UserMiddleware,
    I18nMiddleware,
    BanMiddleware,
    RateLimitMiddleware,
)


# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot) -> None:
    """Установить команды бота."""
    commands_ru = [
        BotCommand(command='start', description='Запустить бота'),
        BotCommand(command='menu', description='Главное меню'),
        BotCommand(command='tariffs', description='Тарифы'),
        BotCommand(command='language', description='Сменить язык'),
    ]
    
    commands_en = [
        BotCommand(command='start', description='Start the bot'),
        BotCommand(command='menu', description='Main menu'),
        BotCommand(command='tariffs', description='Plans'),
        BotCommand(command='language', description='Change language'),
    ]
    
    # Устанавливаем команды для разных языков
    await bot.set_my_commands(commands_ru, language_code='ru')
    await bot.set_my_commands(commands_en, language_code='en')
    await bot.set_my_commands(commands_en)  # По умолчанию


def setup_middlewares() -> None:
    """Настроить middleware."""
    # Порядок важен!
    # 1. Database — первым, чтобы сессия была доступна
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    # 2. User — регистрация пользователя
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    
    # 3. I18n — определение языка
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
    
    # 4. Ban — проверка бана
    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())
    
    # 5. Rate Limit — защита от спама
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())


def setup_routers() -> None:
    """Настроить роутеры."""
    handlers_router = setup_handlers()
    callbacks_router = setup_callbacks()
    
    dp.include_router(handlers_router)
    dp.include_router(callbacks_router)


async def on_startup() -> None:
    """Действия при запуске бота."""
    logger.info("Starting bot...")
    
    # Инициализируем БД
    await init_db()
    logger.info("Database initialized")
    
    # Устанавливаем команды
    await set_commands(bot)
    logger.info("Bot commands set")
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")


async def on_shutdown() -> None:
    """Действия при остановке бота."""
    logger.info("Shutting down bot...")
    await bot.session.close()


async def main() -> None:
    """Главная функция."""
    # Проверяем конфигурацию
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Настраиваем middleware и роутеры
    setup_middlewares()
    setup_routers()
    
    # Регистрируем startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запускаем polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await on_shutdown()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
