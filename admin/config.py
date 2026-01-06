"""Admin panel configuration."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    secret_key: str = "change-this-in-production"
    
    # Database
    database_path: str = "./data/bot.db"
    backup_dir: str = "./data/backups"
    
    # Admin
    admin_ids: str = ""  # Comma-separated telegram IDs
    
    # Webhook
    webhook_base_url: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
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
