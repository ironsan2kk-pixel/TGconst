"""Promocode Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class PromocodeBase(BaseModel):
    """Base promocode schema."""
    code: str = Field(..., min_length=1, max_length=50, description="Promocode")
    discount_percent: int = Field(0, ge=0, le=100, description="Discount percentage")
    discount_amount: float = Field(0.0, ge=0, description="Fixed discount amount")
    max_uses: int | None = Field(None, ge=1, description="Maximum uses, None = unlimited")
    valid_from: datetime | None = Field(None, description="Valid from")
    valid_until: datetime | None = Field(None, description="Valid until")
    tariff_id: int | None = Field(None, description="Specific tariff ID, None = all")
    is_active: bool = Field(True, description="Is active")

    @field_validator('code')
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        return v.upper()


class PromocodeCreate(PromocodeBase):
    """Schema for creating a promocode."""
    pass


class PromocodeUpdate(BaseModel):
    """Schema for updating a promocode."""
    code: str | None = Field(None, min_length=1, max_length=50)
    discount_percent: int | None = Field(None, ge=0, le=100)
    discount_amount: float | None = Field(None, ge=0)
    max_uses: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    tariff_id: int | None = None
    is_active: bool | None = None

    @field_validator('code')
    @classmethod
    def uppercase_code(cls, v: str | None) -> str | None:
        if v:
            return v.upper()
        return v


class TariffShort(BaseModel):
    """Short tariff info."""
    id: int
    name_ru: str
    name_en: str

    class Config:
        from_attributes = True


class PromocodeResponse(BaseModel):
    """Schema for promocode response."""
    id: int
    code: str
    discount_percent: int
    discount_amount: float
    max_uses: int | None
    used_count: int
    valid_from: datetime | None
    valid_until: datetime | None
    tariff: TariffShort | None
    is_active: bool
    is_valid: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PromocodeListResponse(BaseModel):
    """Schema for list of promocodes."""
    items: list[PromocodeResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PromocodeUseResponse(BaseModel):
    """Schema for promocode use record."""
    id: int
    user_id: int
    payment_id: int | None
    used_at: datetime

    class Config:
        from_attributes = True


class PromocodeStats(BaseModel):
    """Promocode statistics."""
    total: int
    active: int
    total_uses: int
    total_discount_given: float
