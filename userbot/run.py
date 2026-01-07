"""
Точка входа для Pyrogram Userbot.

Запускает userbot с проверкой подписок.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from userbot.config import userbot_config
from userbot.client import userbot_client
from bot.services.subscription_checker import SubscriptionChecker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            Path(__file__).parent.parent / 'logs' / 'userbot.log',
            encoding='utf-8',
        ) if (Path(__file__).parent.parent / 'logs').exists() else logging.NullHandler(),
    ]
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Главная функция."""
    logger.info("=" * 50)
    logger.info("Starting Userbot with Subscription Checker")
    logger.info("=" * 50)
    
    # Валидация конфига
    try:
        userbot_config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file")
        return
    
    # Создаём директорию для логов
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Запускаем userbot
    try:
        await userbot_client.start()
        logger.info("Userbot connected successfully!")
    except Exception as e:
        logger.error(f"Failed to start userbot: {e}")
        return
    
    # Создаём и запускаем checker подписок
    checker = SubscriptionChecker()
    
    try:
        # Запускаем проверку в фоне
        checker_task = asyncio.create_task(checker.run_forever())
        
        logger.info("Subscription checker started")
        logger.info("Press Ctrl+C to stop")
        
        # Держим процесс запущенным
        await checker_task
        
    except asyncio.CancelledError:
        logger.info("Shutting down...")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Останавливаем checker
        await checker.stop()
        # Останавливаем userbot
        await userbot_client.stop()
        logger.info("Userbot stopped")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
