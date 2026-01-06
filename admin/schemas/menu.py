"""Menu Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


MenuItemType = Literal["section", "link", "text", "faq", "system"]
SystemAction = Literal["tariffs", "subscriptions", "language", "support", "promocode"]
Visibility = Literal["all", "subscribed", "not_subscribed"]
VisibilityLanguage = Literal["all", "ru", "en"]


class MenuItemBase(BaseModel):
    """Base menu item schema."""
    type: MenuItemType = Field(..., description="Item type")
    system_action: SystemAction | None = Field(None, description="System action for type=system")
    text_ru: str = Field(..., min_length=1, max_length=100, description="Button text RU")
    text_en: str = Field(..., min_length=1, max_length=100, description="Button text EN")
    icon: str | None = Field(None, max_length=10, description="Emoji icon")
    value: str | None = Field(None, description="URL / message text / faq_id")
    visibility: Visibility = Field("all", description="Visibility condition")
    visibility_language: VisibilityLanguage = Field("all", description="Language visibility")
    sort_order: int = Field(0, description="Sort order")
    is_active: bool = Field(True, description="Is active")


class MenuItemCreate(MenuItemBase):
    """Schema for creating a menu item."""
    parent_id: int | None = Field(None, description="Parent menu item ID")


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item."""
    parent_id: int | None = None
    type: MenuItemType | None = None
    system_action: SystemAction | None = None
    text_ru: str | None = Field(None, min_length=1, max_length=100)
    text_en: str | None = Field(None, min_length=1, max_length=100)
    icon: str | None = None
    value: str | None = None
    visibility: Visibility | None = None
    visibility_language: VisibilityLanguage | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class MenuItemReorder(BaseModel):
    """Schema for reordering menu items."""
    items: list[dict] = Field(..., description="List of {id, sort_order, parent_id}")


class MenuItemResponse(MenuItemBase):
    """Schema for menu item response."""
    id: int
    parent_id: int | None
    created_at: datetime
    children: list["MenuItemResponse"] = []

    class Config:
        from_attributes = True


class MenuItemFlatResponse(MenuItemBase):
    """Schema for flat menu item response (without children)."""
    id: int
    parent_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class MenuTreeResponse(BaseModel):
    """Schema for menu tree response."""
    items: list[MenuItemResponse]


class MenuItemListResponse(BaseModel):
    """Schema for list of menu items."""
    items: list[MenuItemFlatResponse]
    total: int


# Update forward references
MenuItemResponse.model_rebuild()
