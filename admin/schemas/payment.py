"""Payment Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Base payment schema."""
    user_id: int = Field(..., description="User ID")
    tariff_id: int = Field(..., description="Tariff ID")
    amount: float = Field(..., ge=0, description="Payment amount")


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    original_amount: float | None = None
    promocode_id: int | None = None
    status: str = Field("pending", description="Payment status")
    payment_method: str = Field("cryptobot", description="Payment method")


class ManualPaymentCreate(BaseModel):
    """Schema for creating a manual payment."""
    user_id: int = Field(..., description="User ID")
    tariff_id: int = Field(..., description="Tariff ID")
    amount: float = Field(..., ge=0, description="Payment amount")
    confirmed_by: int = Field(..., description="Admin telegram ID")


class ManualConfirm(BaseModel):
    """Schema for manually confirming a payment."""
    confirmed_by: int = Field(..., description="Admin telegram ID who confirmed")


class UserShort(BaseModel):
    """Short user info."""
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None

    class Config:
        from_attributes = True


class TariffShort(BaseModel):
    """Short tariff info."""
    id: int
    name_ru: str
    name_en: str
    price: float

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: int
    user: UserShort
    tariff: TariffShort | None
    subscription_id: int | None
    invoice_id: str | None
    amount: float
    original_amount: float | None
    promocode_id: int | None
    status: str
    payment_method: str
    confirmed_by: int | None
    paid_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    """Schema for list of payments."""
    items: list[PaymentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PaymentStats(BaseModel):
    """Payment statistics."""
    total_count: int
    paid_count: int
    pending_count: int
    total_amount: float
    today_amount: float
    month_amount: float


class RevenueByDay(BaseModel):
    """Revenue by day for charts."""
    date: str
    amount: float
    count: int
