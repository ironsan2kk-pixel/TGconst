"""Subscription Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    user_id: int = Field(..., description="User ID")
    tariff_id: int = Field(..., description="Tariff ID")
    is_trial: bool = Field(False, description="Is trial subscription")


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription."""
    days: int | None = Field(None, description="Duration in days, None = use tariff duration")
    granted_by: int | None = Field(None, description="Admin telegram ID who granted")


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""
    is_active: bool | None = None
    expires_at: datetime | None = None


class UserShort(BaseModel):
    """Short user info for subscription response."""
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None

    class Config:
        from_attributes = True


class TariffShort(BaseModel):
    """Short tariff info for subscription response."""
    id: int
    name_ru: str
    name_en: str
    price: float

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""
    id: int
    user: UserShort
    tariff: TariffShort
    is_trial: bool
    starts_at: datetime
    expires_at: datetime | None
    is_active: bool
    auto_kicked: bool
    notified_3days: bool
    notified_1day: bool
    granted_by: int | None
    created_at: datetime
    is_expired: bool

    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Schema for list of subscriptions."""
    items: list[SubscriptionResponse]
    total: int
    page: int
    per_page: int
    pages: int


class SubscriptionStats(BaseModel):
    """Subscription statistics."""
    total: int
    active: int
    expired: int
    trial: int
    forever: int
