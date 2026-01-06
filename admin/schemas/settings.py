"""Settings Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class SettingItem(BaseModel):
    """Single setting item."""
    key: str
    value: str | None
    updated_at: datetime

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    """Schema for updating a setting."""
    value: str | None = Field(None, description="Setting value (JSON string)")


class SettingsBulkUpdate(BaseModel):
    """Schema for bulk updating settings."""
    settings: dict[str, str | None] = Field(..., description="Key-value pairs")


class BotSettings(BaseModel):
    """Bot settings grouped."""
    bot_token: str | None = None
    cryptobot_token: str | None = None
    admin_ids: list[int] = []
    default_language: str = "ru"
    notify_new_users: bool = True
    notify_payments: bool = True


class MessagesSettings(BaseModel):
    """Message settings grouped."""
    welcome_message_ru: str | None = None
    welcome_message_en: str | None = None
    support_url: str | None = None


class SettingsResponse(BaseModel):
    """Full settings response."""
    bot: BotSettings
    messages: MessagesSettings


class SettingsListResponse(BaseModel):
    """List all settings."""
    items: list[SettingItem]
    total: int
