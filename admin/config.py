"""Admin panel configuration."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорировать лишние поля
    )
    
    # Telegram Bot
    bot_token: str = ""
    
    # CryptoBot
    cryptobot_token: str = ""
    cryptobot_webhook_secret: str = ""
    
    # Userbot
    userbot_api_id: str = ""
    userbot_api_hash: str = ""
    userbot_phone: str = ""
    userbot_session_string: str = ""
    
    # Admin
    admin_ids: str = ""  # Comma-separated telegram IDs
    
    # Database
    database_path: str = "./data/bot.db"
    backup_dir: str = "./data/backups"
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8001
    webhook_base_url: str = ""
    
    # App
    debug: bool = False
    secret_key: str = "change-this-in-production"
    default_language: str = "ru"
    
    @property
    def host(self) -> str:
        """Alias for backend_host."""
        return self.backend_host
    
    @property
    def port(self) -> int:
        """Alias for backend_port."""
        return self.backend_port
    
    @property
    def database_url(self) -> str:
        """Get SQLAlchemy database URL."""
        return f"sqlite+aiosqlite:///{self.database_path}"
    
    @property
    def admin_id_list(self) -> list[int]:
        """Get list of admin telegram IDs."""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]


# Create settings instance
settings = Settings()

# Ensure directories exist
Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
Path(settings.backup_dir).mkdir(parents=True, exist_ok=True)
