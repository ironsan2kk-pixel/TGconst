"""User Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema."""
    telegram_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, description="Telegram username")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    language: str = Field("ru", description="User language")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    language: str | None = None
    is_banned: bool | None = None
    ban_reason: str | None = None


class UserBan(BaseModel):
    """Schema for banning a user."""
    reason: str | None = Field(None, description="Ban reason")


class GrantAccess(BaseModel):
    """Schema for granting access to a user."""
    tariff_id: int = Field(..., description="Tariff ID to grant")
    days: int | None = Field(None, description="Days of access, None = use tariff duration")
    is_trial: bool = Field(False, description="Is this a trial subscription")


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_banned: bool
    ban_reason: str | None
    created_at: datetime
    last_activity: datetime
    active_subscriptions_count: int = 0
    total_payments: float = 0

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Schema for detailed user response with subscriptions."""
    subscriptions: list["SubscriptionShort"] = []
    payments: list["PaymentShort"] = []

    class Config:
        from_attributes = True


class SubscriptionShort(BaseModel):
    """Short subscription info."""
    id: int
    tariff_name: str
    is_trial: bool
    starts_at: datetime
    expires_at: datetime | None
    is_active: bool

    class Config:
        from_attributes = True


class PaymentShort(BaseModel):
    """Short payment info."""
    id: int
    amount: float
    status: str
    payment_method: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for list of users."""
    items: list[UserResponse]
    total: int
    page: int
    per_page: int
    pages: int


# Update forward references
UserDetailResponse.model_rebuild()
