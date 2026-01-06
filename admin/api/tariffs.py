"""Tariffs API endpoints."""

from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admin.database import get_session
from admin.schemas.tariff import (
    TariffCreate,
    TariffUpdate,
    TariffResponse,
    TariffListResponse,
    ChannelShort,
)
from bot.models import Tariff, TariffChannel, Channel, Subscription

router = APIRouter(prefix="/tariffs", tags=["Tariffs"])


async def _build_tariff_response(session: AsyncSession, tariff: Tariff) -> TariffResponse:
    """Build tariff response with channels and stats."""
    # Get channels
    result = await session.execute(
        select(Channel).join(TariffChannel).where(
            TariffChannel.tariff_id == tariff.id
        )
    )
    channels = result.scalars().all()
    
    # Get subscriptions count
    subs_count = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.tariff_id == tariff.id,
            Subscription.is_active == True
        )
    )
    
    return TariffResponse(
        id=tariff.id,
        name_ru=tariff.name_ru,
        name_en=tariff.name_en,
        description_ru=tariff.description_ru,
        description_en=tariff.description_en,
        price=tariff.price,
        duration_days=tariff.duration_days,
        trial_days=tariff.trial_days,
        is_active=tariff.is_active,
        sort_order=tariff.sort_order,
        created_at=tariff.created_at,
        channels=[
            ChannelShort(id=c.id, title=c.title, username=c.username)
            for c in channels
        ],
        subscriptions_count=subs_count or 0
    )


@router.get("", response_model=TariffListResponse)
async def get_tariffs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Get list of tariffs with pagination."""
    query = select(Tariff)
    count_query = select(func.count(Tariff.id))
    
    # Filters
    if search:
        query = query.where(
            (Tariff.name_ru.ilike(f"%{search}%")) |
            (Tariff.name_en.ilike(f"%{search}%"))
        )
        count_query = count_query.where(
            (Tariff.name_ru.ilike(f"%{search}%")) |
            (Tariff.name_en.ilike(f"%{search}%"))
        )
    
    if is_active is not None:
        query = query.where(Tariff.is_active == is_active)
        count_query = count_query.where(Tariff.is_active == is_active)
    
    # Count total
    total = await session.scalar(count_query)
    pages = ceil(total / per_page) if total else 1
    
    # Get items
    query = query.order_by(Tariff.sort_order, Tariff.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await session.execute(query)
    tariffs = result.scalars().all()
    
    items = [await _build_tariff_response(session, t) for t in tariffs]
    
    return TariffListResponse(
        items=items,
        total=total or 0,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/{tariff_id}", response_model=TariffResponse)
async def get_tariff(
    tariff_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get tariff by ID."""
    result = await session.execute(
        select(Tariff).where(Tariff.id == tariff_id)
    )
    tariff = result.scalar_one_or_none()
    
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    
    return await _build_tariff_response(session, tariff)


@router.post("", response_model=TariffResponse)
async def create_tariff(
    data: TariffCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new tariff."""
    tariff = Tariff(
        name_ru=data.name_ru,
        name_en=data.name_en,
        description_ru=data.description_ru,
        description_en=data.description_en,
        price=data.price,
        duration_days=data.duration_days,
        trial_days=data.trial_days,
        is_active=data.is_active,
        sort_order=data.sort_order
    )
    session.add(tariff)
    await session.flush()
    
    # Add channel associations
    for channel_id in data.channel_ids:
        tc = TariffChannel(tariff_id=tariff.id, channel_id=channel_id)
        session.add(tc)
    
    await session.commit()
    await session.refresh(tariff)
    
    return await _build_tariff_response(session, tariff)


@router.patch("/{tariff_id}", response_model=TariffResponse)
async def update_tariff(
    tariff_id: int,
    data: TariffUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a tariff."""
    result = await session.execute(
        select(Tariff).where(Tariff.id == tariff_id)
    )
    tariff = result.scalar_one_or_none()
    
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True, exclude={"channel_ids"})
    for field, value in update_data.items():
        setattr(tariff, field, value)
    
    # Update channel associations if provided
    if data.channel_ids is not None:
        # Remove existing
        await session.execute(
            select(TariffChannel).where(TariffChannel.tariff_id == tariff_id)
        )
        result = await session.execute(
            select(TariffChannel).where(TariffChannel.tariff_id == tariff_id)
        )
        for tc in result.scalars().all():
            await session.delete(tc)
        
        # Add new
        for channel_id in data.channel_ids:
            tc = TariffChannel(tariff_id=tariff_id, channel_id=channel_id)
            session.add(tc)
    
    await session.commit()
    await session.refresh(tariff)
    
    return await _build_tariff_response(session, tariff)


@router.delete("/{tariff_id}")
async def delete_tariff(
    tariff_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a tariff."""
    result = await session.execute(
        select(Tariff).where(Tariff.id == tariff_id)
    )
    tariff = result.scalar_one_or_none()
    
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    
    await session.delete(tariff)
    await session.commit()
    
    return {"status": "ok", "message": "Tariff deleted"}
