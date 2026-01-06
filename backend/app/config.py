"""
Конфигурация приложения через pydantic-settings
"""
from pathlib import Path
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта (на уровень выше backend/)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # === APP ===
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    
    # === PATHS ===
    DATA_DIR: Path = Path("./data")
    MAIN_DB_PATH: Path = Path("./data/main.db")
    
    # === JWT ===
    JWT_SECRET_KEY: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # === ADMIN ===
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # === USERBOT ===
    USERBOT_API_ID: int = 0
    USERBOT_API_HASH: str = ""
    USERBOT_PHONE: str = ""
    USERBOT_SESSION_STRING: str = ""
    
    # === SERVER ===
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    WEBHOOK_BASE_URL: str = ""
    
    @model_validator(mode="after")
    def resolve_paths(self) -> "Settings":
        """Преобразование относительных путей в абсолютные"""
        # Если пути относительные, делаем их относительно PROJECT_ROOT
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
    
    def get_bot_dir(self, bot_uuid: str) -> Path:
        """Папка конкретного бота"""
        return self.bots_dir / bot_uuid


@lru_cache
def get_settings() -> Settings:
    """Получить настройки (с кешированием)"""
    return Settings()
