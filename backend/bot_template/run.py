"""
Точка входа для запуска бота.
Использование: python run.py --bot-uuid=<uuid>
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импортов
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.bot_template.config import load_bot_config
from backend.bot_template.loader import create_bot, create_dispatcher
from backend.bot_template.database import init_database, close_database
from backend.bot_template.handlers import register_all_handlers


# Настройка логирования
def setup_logging(bot_uuid: str, debug: bool = False):
    """Настройка логирования для бота"""
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Папка для логов
    log_dir = PROJECT_ROOT / "data" / "bots" / bot_uuid / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Форматтер
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Хендлер для файла
    file_handler = logging.FileHandler(
        log_dir / "bot.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Уменьшаем шум от библиотек
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logging.getLogger(f"bot.{bot_uuid[:8]}")


async def main(bot_uuid: str):
    """Главная функция запуска бота"""
    logger = setup_logging(bot_uuid)
    logger.info(f"Запуск бота {bot_uuid}")
    
    try:
        # Загружаем конфигурацию бота из main.db
        config = await load_bot_config(bot_uuid)
        if not config:
            logger.error(f"Бот {bot_uuid} не найден в базе данных")
            sys.exit(1)
        
        logger.info(f"Конфигурация загружена: {config['name']}")
        
        # Инициализируем базу данных бота
        await init_database(bot_uuid)
        logger.info("База данных инициализирована")
        
        # Создаём бота и диспетчер
        bot = create_bot(config['bot_token'])
        dp = create_dispatcher()
        
        # Регистрируем все хендлеры
        register_all_handlers(dp)
        logger.info("Хендлеры зарегистрированы")
        
        # Запускаем polling
        logger.info("Бот запущен и готов к работе")
        
        # Удаляем webhook если был
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запускаем polling с передачей конфига
        await dp.start_polling(
            bot, 
            allowed_updates=dp.resolve_used_update_types(),
            bot_uuid=bot_uuid,
            bot_config=config
        )
        
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        await close_database()
        logger.info("Бот остановлен")


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Telegram Bot from Constructor")
    parser.add_argument(
        "--bot-uuid",
        required=True,
        help="UUID бота из базы данных"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    try:
        asyncio.run(main(args.bot_uuid))
    except KeyboardInterrupt:
        print("\nБот остановлен по Ctrl+C")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
