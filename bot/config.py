"""
Конфигурация Telegram бота.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()


class Config:
    """Конфигурация бота."""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    # Admin IDs
    ADMIN_IDS: list[int] = [
        int(x.strip()) 
        for x in os.getenv('ADMIN_IDS', '').split(',') 
        if x.strip().isdigit()
    ]
    
    # CryptoBot
    CRYPTOBOT_TOKEN: str = os.getenv('CRYPTOBOT_TOKEN', '')
    CRYPTOBOT_WEBHOOK_SECRET: str = os.getenv('CRYPTOBOT_WEBHOOK_SECRET', '')
    
    # Database
    BASE_DIR: Path = Path(__file__).parent.parent
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'bot.db'))
    
    # Settings
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    DEFAULT_LANGUAGE: str = os.getenv('DEFAULT_LANGUAGE', 'ru')
    
    # Support
    SUPPORT_URL: str = os.getenv('SUPPORT_URL', '')
    
    # Rate limiting
    RATE_LIMIT_MESSAGES: int = 30  # сообщений
    RATE_LIMIT_PERIOD: int = 60    # секунд
    
    # Notifications settings
    NOTIFY_NEW_USERS: bool = True
    NOTIFY_PAYMENTS: bool = True
    
    @classmethod
    def validate(cls) -> bool:
        """Проверить обязательные настройки."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not cls.ADMIN_IDS:
            raise ValueError("ADMIN_IDS is required")
        return True


config = Config()
