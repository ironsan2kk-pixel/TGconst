"""
Admin Panel Configuration
Настройки для FastAPI backend
"""

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки админ-панели"""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    SECRET_KEY: str = "your-super-secret-key-change-this"
    
    # Database
    DATABASE_PATH: str = "./data/bot.db"
    BACKUP_DIR: str = "./data/backups"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Bot token (для проверки)
    BOT_TOKEN: str = ""
    
    # Admin IDs
    ADMIN_IDS: str = ""  # Comma-separated
    
    @property
    def database_url(self) -> str:
        """SQLite URL для SQLAlchemy"""
        return f"sqlite+aiosqlite:///{self.DATABASE_PATH}"
    
    @property
    def admin_ids_list(self) -> list[int]:
        """Список admin IDs"""
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]
    
    @property
    def backup_path(self) -> Path:
        """Путь к директории бэкапов"""
        path = Path(self.BACKUP_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки (с кешированием)"""
    return Settings()


# Singleton
settings = get_settings()
