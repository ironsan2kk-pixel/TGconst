"""Users API endpoints."""

from math import ceil
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from admin.schemas.user import (
    UserUpdate,
    UserBan,
    GrantAccess,
    UserResponse,
    UserDetailResponse,
    UserListResponse,
    SubscriptionShort,
    PaymentShort,
)
from bot.models import User, Subscription, Payment, Tariff

router = APIRouter()


async def _build_user_response(session: AsyncSession, user: User) -> UserResponse:
    """Build user response with stats."""
    # Active subscriptions count
    active_subs = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        )
    )
    
    # Total payments
    total_payments = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.user_id == user.id,
            Payment.status == "paid"
        )
    )
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language=user.language,
        is_banned=user.is_banned,
        ban_reason=user.ban_reason,
        created_at=user.created_at,
        last_activity=user.last_activity,
        active_subscriptions_count=active_subs or 0,
        total_payments=float(total_payments or 0)
    )


@router.get("", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    is_banned: bool | None = None,
    has_subscription: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Get list of users with pagination."""
    query = select(User)
    count_query = select(func.count(User.id))
    
    # Search
    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.telegram_id == int(search) if search.isdigit() else False
            )
        )
        count_query = count_query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.telegram_id == int(search) if search.isdigit() else False
            )
        )
    
    # Banned filter
    if is_banned is not None:
        query = query.where(User.is_banned == is_banned)
        count_query = count_query.where(User.is_banned == is_banned)
    
    # Has subscription filter
    if has_subscription is not None:
        subquery = select(Subscription.user_id).where(Subscription.is_active == True).distinct()
        if has_subscription:
            query = query.where(User.id.in_(subquery))
            count_query = count_query.where(User.id.in_(subquery))
        else:
            query = query.where(User.id.notin_(subquery))
            count_query = count_query.where(User.id.notin_(subquery))
    
    # Count total
    total = await session.scalar(count_query)
    pages = ceil(total / per_page) if total else 1
    
    # Get items
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await session.execute(query)
    users = result.scalars().all()
    
    items = [await _build_user_response(session, u) for u in users]
    
    return UserListResponse(
        items=items,
        total=total or 0,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get user details by ID."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscriptions
    subs_result = await session.execute(
        select(Subscription, Tariff).join(Tariff).where(
            Subscription.user_id == user_id
        ).order_by(Subscription.created_at.desc())
    )
    subscriptions = []
    for sub, tariff in subs_result:
        subscriptions.append(SubscriptionShort(
            id=sub.id,
            tariff_name=tariff.name_ru,
            is_trial=sub.is_trial,
            starts_at=sub.starts_at,
            expires_at=sub.expires_at,
            is_active=sub.is_active
        ))
    
    # Get payments
    payments_result = await session.execute(
        select(Payment).where(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).limit(20)
    )
    payments = [
        PaymentShort(
            id=p.id,
            amount=p.amount,
            status=p.status,
            payment_method=p.payment_method,
            created_at=p.created_at
        )
        for p in payments_result.scalars().all()
    ]
    
    base = await _build_user_response(session, user)
    
    return UserDetailResponse(
        **base.model_dump(),
        subscriptions=subscriptions,
        payments=payments
    )


@router.get("/by-telegram/{telegram_id}", response_model=UserDetailResponse)
async def get_user_by_telegram(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get user by Telegram ID."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await get_user(user.id, session)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update user."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await session.commit()
    await session.refresh(user)
    
    return await _build_user_response(session, user)


@router.post("/{user_id}/ban")
async def ban_user(
    user_id: int,
    data: UserBan,
    session: AsyncSession = Depends(get_session)
):
    """Ban user."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_banned = True
    user.ban_reason = data.reason
    
    await session.commit()
    
    return {"status": "ok", "message": "User banned"}


@router.post("/{user_id}/unban")
async def unban_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Unban user."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_banned = False
    user.ban_reason = None
    
    await session.commit()
    
    return {"status": "ok", "message": "User unbanned"}


@router.post("/{user_id}/grant-access")
async def grant_access(
    user_id: int,
    data: GrantAccess,
    admin_telegram_id: int = Query(..., description="Admin telegram ID"),
    session: AsyncSession = Depends(get_session)
):
    """Grant subscription access to user."""
    # Check user exists
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check tariff exists
    result = await session.execute(
        select(Tariff).where(Tariff.id == data.tariff_id)
    )
    tariff = result.scalar_one_or_none()
    
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    
    # Calculate expiration
    now = datetime.utcnow()
    days = data.days if data.days is not None else tariff.duration_days
    expires_at = None if days == 0 else now + timedelta(days=days)
    
    # Create subscription
    subscription = Subscription(
        user_id=user_id,
        tariff_id=data.tariff_id,
        is_trial=data.is_trial,
        starts_at=now,
        expires_at=expires_at,
        is_active=True,
        granted_by=admin_telegram_id
    )
    session.add(subscription)
    await session.commit()
    
    return {
        "status": "ok",
        "message": "Access granted",
        "subscription_id": subscription.id
    }


@router.post("/{user_id}/revoke-access")
async def revoke_access(
    user_id: int,
    tariff_id: int = Query(..., description="Tariff ID to revoke"),
    session: AsyncSession = Depends(get_session)
):
    """Revoke subscription access from user."""
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.tariff_id == tariff_id,
            Subscription.is_active == True
        )
    )
    subscriptions = result.scalars().all()
    
    if not subscriptions:
        raise HTTPException(status_code=404, detail="Active subscription not found")
    
    for sub in subscriptions:
        sub.is_active = False
        sub.expires_at = datetime.utcnow()
    
    await session.commit()
    
    return {"status": "ok", "message": "Access revoked"}
