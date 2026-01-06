"""Subscriptions API endpoints."""

from math import ceil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from admin.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionListResponse,
    SubscriptionStats,
    UserShort,
    TariffShort,
)
from bot.models import Subscription, User, Tariff

router = APIRouter()


async def _build_subscription_response(
    session: AsyncSession, 
    sub: Subscription
) -> SubscriptionResponse:
    """Build subscription response."""
    # Get user
    user_result = await session.execute(
        select(User).where(User.id == sub.user_id)
    )
    user = user_result.scalar_one()
    
    # Get tariff
    tariff_result = await session.execute(
        select(Tariff).where(Tariff.id == sub.tariff_id)
    )
    tariff = tariff_result.scalar_one()
    
    now = datetime.utcnow()
    is_expired = sub.expires_at is not None and now > sub.expires_at
    
    return SubscriptionResponse(
        id=sub.id,
        user=UserShort(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name
        ),
        tariff=TariffShort(
            id=tariff.id,
            name_ru=tariff.name_ru,
            name_en=tariff.name_en,
            price=tariff.price
        ),
        is_trial=sub.is_trial,
        starts_at=sub.starts_at,
        expires_at=sub.expires_at,
        is_active=sub.is_active,
        auto_kicked=sub.auto_kicked,
        notified_3days=sub.notified_3days,
        notified_1day=sub.notified_1day,
        granted_by=sub.granted_by,
        created_at=sub.created_at,
        is_expired=is_expired
    )


@router.get("", response_model=SubscriptionListResponse)
async def get_subscriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    tariff_id: int | None = None,
    is_active: bool | None = None,
    is_trial: bool | None = None,
    is_expired: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Get list of subscriptions with pagination."""
    now = datetime.utcnow()
    
    query = select(Subscription)
    count_query = select(func.count(Subscription.id))
    
    # Filters
    if user_id is not None:
        query = query.where(Subscription.user_id == user_id)
        count_query = count_query.where(Subscription.user_id == user_id)
    
    if tariff_id is not None:
        query = query.where(Subscription.tariff_id == tariff_id)
        count_query = count_query.where(Subscription.tariff_id == tariff_id)
    
    if is_active is not None:
        query = query.where(Subscription.is_active == is_active)
        count_query = count_query.where(Subscription.is_active == is_active)
    
    if is_trial is not None:
        query = query.where(Subscription.is_trial == is_trial)
        count_query = count_query.where(Subscription.is_trial == is_trial)
    
    if is_expired is not None:
        if is_expired:
            query = query.where(
                Subscription.expires_at.isnot(None),
                Subscription.expires_at < now
            )
            count_query = count_query.where(
                Subscription.expires_at.isnot(None),
                Subscription.expires_at < now
            )
        else:
            query = query.where(
                or_(
                    Subscription.expires_at.is_(None),
                    Subscription.expires_at >= now
                )
            )
            count_query = count_query.where(
                or_(
                    Subscription.expires_at.is_(None),
                    Subscription.expires_at >= now
                )
            )
    
    # Count total
    total = await session.scalar(count_query)
    pages = ceil(total / per_page) if total else 1
    
    # Get items
    query = query.order_by(Subscription.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await session.execute(query)
    subscriptions = result.scalars().all()
    
    items = [await _build_subscription_response(session, s) for s in subscriptions]
    
    return SubscriptionListResponse(
        items=items,
        total=total or 0,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/stats", response_model=SubscriptionStats)
async def get_subscription_stats(session: AsyncSession = Depends(get_session)):
    """Get subscription statistics."""
    now = datetime.utcnow()
    
    # Total
    total = await session.scalar(select(func.count(Subscription.id)))
    
    # Active (is_active=True and not expired)
    active = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.is_active == True,
            or_(
                Subscription.expires_at.is_(None),
                Subscription.expires_at >= now
            )
        )
    )
    
    # Expired
    expired = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.expires_at.isnot(None),
            Subscription.expires_at < now
        )
    )
    
    # Trial
    trial = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.is_trial == True,
            Subscription.is_active == True
        )
    )
    
    # Forever (no expiration)
    forever = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.expires_at.is_(None),
            Subscription.is_active == True
        )
    )
    
    return SubscriptionStats(
        total=total or 0,
        active=active or 0,
        expired=expired or 0,
        trial=trial or 0,
        forever=forever or 0
    )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get subscription by ID."""
    result = await session.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return await _build_subscription_response(session, subscription)


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    data: SubscriptionUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update subscription."""
    result = await session.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    await session.commit()
    await session.refresh(subscription)
    
    return await _build_subscription_response(session, subscription)


@router.post("/{subscription_id}/deactivate")
async def deactivate_subscription(
    subscription_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Deactivate subscription."""
    result = await session.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = False
    await session.commit()
    
    return {"status": "ok", "message": "Subscription deactivated"}


@router.post("/{subscription_id}/activate")
async def activate_subscription(
    subscription_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Activate subscription."""
    result = await session.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = True
    await session.commit()
    
    return {"status": "ok", "message": "Subscription activated"}


@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete subscription."""
    result = await session.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    await session.delete(subscription)
    await session.commit()
    
    return {"status": "ok", "message": "Subscription deleted"}
