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
    type: MenuItemType = Field("link", description="Item type")
    system_action: SystemAction | str | None = Field(None, description="System action for type=system")
    text_ru: str = Field(..., min_length=1, max_length=100, description="Button text RU")
    text_en: str | None = Field(None, max_length=100, description="Button text EN")
    icon: str | None = Field(None, max_length=10, description="Emoji icon")
    value: str | None = Field(None, description="URL / message text / faq_id")
    photo_file_id: str | None = Field(None, max_length=255, description="Photo file_id for text+photo")
    visibility: Visibility | str = Field("all", description="Visibility condition")
    visibility_language: VisibilityLanguage | str = Field("all", description="Language visibility")
    sort_order: int = Field(0, description="Sort order")
    is_active: bool = Field(True, description="Is active")


class MenuItemCreate(MenuItemBase):
    """Schema for creating a menu item."""
    parent_id: int | None = Field(None, description="Parent menu item ID")


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item."""
    parent_id: int | None = None
    type: MenuItemType | str | None = None
    system_action: SystemAction | str | None = None
    text_ru: str | None = Field(None, min_length=1, max_length=100)
    text_en: str | None = Field(None, max_length=100)
    icon: str | None = None
    value: str | None = None
    photo_file_id: str | None = None
    visibility: Visibility | str | None = None
    visibility_language: VisibilityLanguage | str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class MenuItemReorder(BaseModel):
    """Schema for reordering menu items."""
    items: list[dict] = Field(..., description="List of {id, sort_order, parent_id}")


class MenuItemResponse(BaseModel):
    """Menu item response schema."""
    id: int
    parent_id: int | None
    type: str
    system_action: str | None
    text_ru: str
    text_en: str | None
    icon: str | None
    value: str | None
    photo_file_id: str | None
    visibility: str
    visibility_language: str
    sort_order: int
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


# === Menu Templates ===

class MenuTemplateBase(BaseModel):
    """Base template schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description_ru: str | None = None
    description_en: str | None = None
    template_data: str = Field(..., description="JSON structure of menu items")
    is_active: bool = True


class MenuTemplateCreate(MenuTemplateBase):
    """Schema for creating a template."""
    pass


class MenuTemplateResponse(MenuTemplateBase):
    """Template response schema."""
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True
