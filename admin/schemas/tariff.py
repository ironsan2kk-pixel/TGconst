"""Tariff Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class TariffBase(BaseModel):
    """Base tariff schema."""
    name_ru: str = Field(..., min_length=1, max_length=255, description="Name in Russian")
    name_en: str = Field(..., min_length=1, max_length=255, description="Name in English")
    description_ru: str | None = Field(None, description="Description in Russian")
    description_en: str | None = Field(None, description="Description in English")
    price: float = Field(..., ge=0, description="Price in USDT")
    duration_days: int = Field(30, ge=0, description="Duration in days, 0 = forever")
    trial_days: int = Field(0, ge=0, description="Trial period in days, 0 = no trial")
    is_active: bool = Field(True, description="Is tariff active")
    sort_order: int = Field(0, description="Sort order")


class TariffCreate(TariffBase):
    """Schema for creating a tariff."""
    channel_ids: list[int] = Field(default_factory=list, description="List of channel IDs")


class TariffUpdate(BaseModel):
    """Schema for updating a tariff."""
    name_ru: str | None = Field(None, min_length=1, max_length=255)
    name_en: str | None = Field(None, min_length=1, max_length=255)
    description_ru: str | None = None
    description_en: str | None = None
    price: float | None = Field(None, ge=0)
    duration_days: int | None = Field(None, ge=0)
    trial_days: int | None = Field(None, ge=0)
    is_active: bool | None = None
    sort_order: int | None = None
    channel_ids: list[int] | None = None


class ChannelShort(BaseModel):
    """Short channel info for tariff response."""
    id: int
    title: str
    username: str | None

    class Config:
        from_attributes = True


class TariffResponse(TariffBase):
    """Schema for tariff response."""
    id: int
    created_at: datetime
    channels: list[ChannelShort] = []
    subscriptions_count: int = 0

    class Config:
        from_attributes = True


class TariffListResponse(BaseModel):
    """Schema for list of tariffs."""
    items: list[TariffResponse]
    total: int
    page: int
    per_page: int
    pages: int
