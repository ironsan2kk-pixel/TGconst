"""FAQ Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class FAQItemBase(BaseModel):
    """Base FAQ item schema."""
    question_ru: str = Field(..., min_length=1, max_length=500, description="Question RU")
    question_en: str = Field(..., min_length=1, max_length=500, description="Question EN")
    answer_ru: str = Field(..., min_length=1, description="Answer RU")
    answer_en: str = Field(..., min_length=1, description="Answer EN")
    category_id: int | None = Field(None, description="Menu item category ID")
    sort_order: int = Field(0, description="Sort order")
    is_active: bool = Field(True, description="Is active")


class FAQItemCreate(FAQItemBase):
    """Schema for creating a FAQ item."""
    pass


class FAQItemUpdate(BaseModel):
    """Schema for updating a FAQ item."""
    question_ru: str | None = Field(None, min_length=1, max_length=500)
    question_en: str | None = Field(None, min_length=1, max_length=500)
    answer_ru: str | None = Field(None, min_length=1)
    answer_en: str | None = Field(None, min_length=1)
    category_id: int | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryShort(BaseModel):
    """Short category info."""
    id: int
    text_ru: str
    text_en: str

    class Config:
        from_attributes = True


class FAQItemResponse(FAQItemBase):
    """Schema for FAQ item response."""
    id: int
    category: CategoryShort | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class FAQItemListResponse(BaseModel):
    """Schema for list of FAQ items."""
    items: list[FAQItemResponse]
    total: int
    page: int
    per_page: int
    pages: int


class FAQStats(BaseModel):
    """FAQ statistics."""
    total: int
    active: int
    by_category: dict[str, int]
