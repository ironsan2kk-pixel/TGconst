"""
Конфигурация Pyrogram Userbot.

Userbot используется для добавления и удаления пользователей из каналов.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()


class UserbotConfig:
    """Конфигурация userbot."""
    
    # Pyrogram API credentials (получить на my.telegram.org)
    API_ID: int = int(os.getenv('USERBOT_API_ID', '0'))
    API_HASH: str = os.getenv('USERBOT_API_HASH', '')
    
    # Телефон для авторизации (формат: +79001234567)
    PHONE: str = os.getenv('USERBOT_PHONE', '')
    
    # Session string (после первой авторизации)
    SESSION_STRING: str = os.getenv('USERBOT_SESSION_STRING', '')
    
    # Имя сессии
    SESSION_NAME: str = 'channel_bot_userbot'
    
    # Путь к файлу сессии (если не используется session string)
    BASE_DIR: Path = Path(__file__).parent.parent
    SESSION_DIR: Path = BASE_DIR / 'data'
    
    # Database
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'bot.db'))
    
    # Таймауты
    INVITE_DELAY: float = 1.0  # Задержка между инвайтами (секунды)
    KICK_DELAY: float = 0.5    # Задержка между киками
    
    # Ретраи
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 5.0
    
    @classmethod
    def validate(cls) -> bool:
        """Проверить обязательные настройки."""
        if not cls.API_ID or cls.API_ID == 0:
            raise ValueError("USERBOT_API_ID is required")
        if not cls.API_HASH:
            raise ValueError("USERBOT_API_HASH is required")
        if not cls.SESSION_STRING and not cls.PHONE:
            raise ValueError("Either USERBOT_SESSION_STRING or USERBOT_PHONE is required")
        return True
    
    @classmethod
    def has_session_string(cls) -> bool:
        """Проверить наличие session string."""
        return bool(cls.SESSION_STRING and len(cls.SESSION_STRING) > 50)


userbot_config = UserbotConfig()
