"""Channel Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class ChannelBase(BaseModel):
    """Base channel schema."""
    channel_id: int = Field(..., description="Telegram channel ID")
    username: str | None = Field(None, description="Channel username without @")
    title: str = Field(..., min_length=1, max_length=255, description="Channel title")
    description: str | None = Field(None, description="Channel description")
    invite_link: str | None = Field(None, description="Invite link")
    is_active: bool = Field(True, description="Is channel active")


class ChannelCreate(ChannelBase):
    """Schema for creating a channel."""
    pass


class ChannelUpdate(BaseModel):
    """Schema for updating a channel."""
    channel_id: int | None = None
    username: str | None = None
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    invite_link: str | None = None
    is_active: bool | None = None


class ChannelResponse(ChannelBase):
    """Schema for channel response."""
    id: int
    created_at: datetime
    tariffs_count: int = 0

    class Config:
        from_attributes = True


class ChannelListResponse(BaseModel):
    """Schema for list of channels."""
    items: list[ChannelResponse]
    total: int
    page: int
    per_page: int
    pages: int
