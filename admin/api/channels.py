"""Channels API endpoints."""

from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admin.database import get_session
from admin.schemas.channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelListResponse,
)
from bot.models import Channel, TariffChannel

router = APIRouter()


@router.get("", response_model=ChannelListResponse)
async def get_channels(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Get list of channels with pagination."""
    query = select(Channel)
    count_query = select(func.count(Channel.id))
    
    # Filters
    if search:
        query = query.where(
            (Channel.title.ilike(f"%{search}%")) |
            (Channel.username.ilike(f"%{search}%"))
        )
        count_query = count_query.where(
            (Channel.title.ilike(f"%{search}%")) |
            (Channel.username.ilike(f"%{search}%"))
        )
    
    if is_active is not None:
        query = query.where(Channel.is_active == is_active)
        count_query = count_query.where(Channel.is_active == is_active)
    
    # Count total
    total = await session.scalar(count_query)
    pages = ceil(total / per_page) if total else 1
    
    # Get items
    query = query.order_by(Channel.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await session.execute(query)
    channels = result.scalars().all()
    
    # Get tariffs count for each channel
    items = []
    for channel in channels:
        tariffs_count = await session.scalar(
            select(func.count(TariffChannel.id)).where(
                TariffChannel.channel_id == channel.id
            )
        )
        items.append(ChannelResponse(
            id=channel.id,
            channel_id=channel.channel_id,
            username=channel.username,
            title=channel.title,
            description=channel.description,
            invite_link=channel.invite_link,
            is_active=channel.is_active,
            created_at=channel.created_at,
            tariffs_count=tariffs_count or 0
        ))
    
    return ChannelListResponse(
        items=items,
        total=total or 0,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get channel by ID."""
    result = await session.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    tariffs_count = await session.scalar(
        select(func.count(TariffChannel.id)).where(
            TariffChannel.channel_id == channel.id
        )
    )
    
    return ChannelResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        username=channel.username,
        title=channel.title,
        description=channel.description,
        invite_link=channel.invite_link,
        is_active=channel.is_active,
        created_at=channel.created_at,
        tariffs_count=tariffs_count or 0
    )


@router.post("", response_model=ChannelResponse)
async def create_channel(
    data: ChannelCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new channel."""
    # Check if channel_id already exists
    existing = await session.scalar(
        select(Channel).where(Channel.channel_id == data.channel_id)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Channel ID already exists")
    
    channel = Channel(
        channel_id=data.channel_id,
        username=data.username,
        title=data.title,
        description=data.description,
        invite_link=data.invite_link,
        is_active=data.is_active
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    
    return ChannelResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        username=channel.username,
        title=channel.title,
        description=channel.description,
        invite_link=channel.invite_link,
        is_active=channel.is_active,
        created_at=channel.created_at,
        tariffs_count=0
    )


@router.patch("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    data: ChannelUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a channel."""
    result = await session.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check for duplicate channel_id
    if data.channel_id and data.channel_id != channel.channel_id:
        existing = await session.scalar(
            select(Channel).where(Channel.channel_id == data.channel_id)
        )
        if existing:
            raise HTTPException(status_code=400, detail="Channel ID already exists")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)
    
    await session.commit()
    await session.refresh(channel)
    
    tariffs_count = await session.scalar(
        select(func.count(TariffChannel.id)).where(
            TariffChannel.channel_id == channel.id
        )
    )
    
    return ChannelResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        username=channel.username,
        title=channel.title,
        description=channel.description,
        invite_link=channel.invite_link,
        is_active=channel.is_active,
        created_at=channel.created_at,
        tariffs_count=tariffs_count or 0
    )


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a channel."""
    result = await session.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    await session.delete(channel)
    await session.commit()
    
    return {"status": "ok", "message": "Channel deleted"}
