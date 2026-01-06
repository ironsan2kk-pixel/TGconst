"""
Конфигурация Userbot через pydantic-settings
"""

from pathlib import Path
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Корень проекта (на уровень выше userbot/)
PROJECT_ROOT = Path(__file__).parent.parent


class UserbotSettings(BaseSettings):
    """Настройки Userbot"""
    
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # === USERBOT (Pyrogram) ===
    USERBOT_API_ID: int = 0
    USERBOT_API_HASH: str = ""
    USERBOT_PHONE: str = ""
    USERBOT_SESSION_STRING: str = ""
    
    # === USERBOT SERVER ===
    USERBOT_HOST: str = "127.0.0.1"
    USERBOT_PORT: int = 8001
    
    # === PATHS ===
    DATA_DIR: Path = Path("./data")
    MAIN_DB_PATH: Path = Path("./data/main.db")
    
    # === RETRY SETTINGS ===
    INVITE_MAX_RETRIES: int = 3
    INVITE_RETRY_DELAY: int = 5  # секунд
    FLOOD_WAIT_MULTIPLIER: float = 1.2  # множитель для FloodWait
    
    @model_validator(mode="after")
    def resolve_paths(self) -> "UserbotSettings":
        """Преобразование относительных путей в абсолютные"""
        if not self.DATA_DIR.is_absolute():
            self.DATA_DIR = PROJECT_ROOT / self.DATA_DIR
        if not self.MAIN_DB_PATH.is_absolute():
            self.MAIN_DB_PATH = PROJECT_ROOT / self.MAIN_DB_PATH
        return self
    
    @property
    def bots_dir(self) -> Path:
        """Папка с данными ботов"""
        return self.DATA_DIR / "bots"
    
    def get_bot_db_path(self, bot_uuid: str) -> Path:
        """Путь к базе данных конкретного бота"""
        return self.bots_dir / bot_uuid / "bot.db"
    
    @property
    def is_configured(self) -> bool:
        """Проверка что userbot настроен"""
        return bool(
            self.USERBOT_API_ID and 
            self.USERBOT_API_HASH and 
            (self.USERBOT_SESSION_STRING or self.USERBOT_PHONE)
        )


@lru_cache
def get_settings() -> UserbotSettings:
    """Получить настройки (с кешированием)"""
    return UserbotSettings()
