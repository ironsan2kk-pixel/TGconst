"""Bot configuration from environment variables."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Telegram Bot
    bot_token: str = ""
    
    # Userbot (Pyrogram)
    userbot_api_id: int = 0
    userbot_api_hash: str = ""
    userbot_phone: str = ""
    userbot_session_string: str = ""
    
    # Admin IDs
    admin_ids: str = ""
    
    # Crypto Wallets
    ton_wallet: str = ""
    trc20_wallet: str = ""
    
    # Database
    database_path: str = "./data/bot.db"
    backup_dir: str = "./data/backups"
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # App
    debug: bool = True
    secret_key: str = "change-this-secret-key"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Get list of admin Telegram IDs."""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]
    
    @property
    def database_url(self) -> str:
        """Get SQLite database URL."""
        return f"sqlite+aiosqlite:///{self.database_path}"
    
    @property
    def database_sync_url(self) -> str:
        """Get synchronous SQLite database URL (for alembic)."""
        return f"sqlite:///{self.database_path}"
    
    def ensure_dirs(self) -> None:
        """Create necessary directories."""
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
