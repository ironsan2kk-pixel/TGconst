"""Export API endpoints for CSV export."""

import csv
import io
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from bot.models import User, Subscription, Payment, Promocode, Tariff

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/users")
async def export_users(
    is_banned: bool | None = None,
    has_subscription: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Export users to CSV."""
    query = select(User)
    
    if is_banned is not None:
        query = query.where(User.is_banned == is_banned)
    
    if has_subscription is not None:
        subquery = select(Subscription.user_id).where(Subscription.is_active == True).distinct()
        if has_subscription:
            query = query.where(User.id.in_(subquery))
        else:
            query = query.where(User.id.notin_(subquery))
    
    query = query.order_by(User.created_at.desc())
    result = await session.execute(query)
    users = result.scalars().all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID", "Telegram ID", "Username", "First Name", "Last Name",
        "Language", "Is Banned", "Ban Reason", "Created At", "Last Activity"
    ])
    
    # Data
    for user in users:
        writer.writerow([
            user.id,
            user.telegram_id,
            user.username or "",
            user.first_name or "",
            user.last_name or "",
            user.language,
            user.is_banned,
            user.ban_reason or "",
            user.created_at.isoformat(),
            user.last_activity.isoformat()
        ])
    
    output.seek(0)
    
    filename = f"users_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/subscriptions")
async def export_subscriptions(
    is_active: bool | None = None,
    tariff_id: int | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Export subscriptions to CSV."""
    query = select(Subscription, User, Tariff).join(
        User, Subscription.user_id == User.id
    ).join(
        Tariff, Subscription.tariff_id == Tariff.id
    )
    
    if is_active is not None:
        query = query.where(Subscription.is_active == is_active)
    
    if tariff_id is not None:
        query = query.where(Subscription.tariff_id == tariff_id)
    
    query = query.order_by(Subscription.created_at.desc())
    result = await session.execute(query)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID", "User ID", "Telegram ID", "Username", "Tariff",
        "Is Trial", "Starts At", "Expires At", "Is Active", "Created At"
    ])
    
    # Data
    for sub, user, tariff in result:
        writer.writerow([
            sub.id,
            user.id,
            user.telegram_id,
            user.username or "",
            tariff.name_ru,
            sub.is_trial,
            sub.starts_at.isoformat(),
            sub.expires_at.isoformat() if sub.expires_at else "Forever",
            sub.is_active,
            sub.created_at.isoformat()
        ])
    
    output.seek(0)
    
    filename = f"subscriptions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/payments")
async def export_payments(
    status: str | None = None,
    payment_method: str | None = None,
    date_from: str | None = Query(None, description="YYYY-MM-DD"),
    date_to: str | None = Query(None, description="YYYY-MM-DD"),
    session: AsyncSession = Depends(get_session)
):
    """Export payments to CSV."""
    query = select(Payment, User).join(
        User, Payment.user_id == User.id
    )
    
    if status:
        query = query.where(Payment.status == status)
    
    if payment_method:
        query = query.where(Payment.payment_method == payment_method)
    
    if date_from:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.where(Payment.created_at >= dt_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            dt_to = datetime.strptime(date_to, "%Y-%m-%d")
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
            query = query.where(Payment.created_at <= dt_to)
        except ValueError:
            pass
    
    query = query.order_by(Payment.created_at.desc())
    result = await session.execute(query)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID", "User ID", "Telegram ID", "Username", "Amount",
        "Original Amount", "Status", "Payment Method", "Paid At", "Created At"
    ])
    
    # Data
    for payment, user in result:
        writer.writerow([
            payment.id,
            user.id,
            user.telegram_id,
            user.username or "",
            payment.amount,
            payment.original_amount or "",
            payment.status,
            payment.payment_method,
            payment.paid_at.isoformat() if payment.paid_at else "",
            payment.created_at.isoformat()
        ])
    
    output.seek(0)
    
    filename = f"payments_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/promocodes")
async def export_promocodes(
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Export promocodes to CSV."""
    query = select(Promocode)
    
    if is_active is not None:
        query = query.where(Promocode.is_active == is_active)
    
    query = query.order_by(Promocode.created_at.desc())
    result = await session.execute(query)
    promocodes = result.scalars().all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID", "Code", "Discount %", "Discount Amount", "Max Uses",
        "Used Count", "Valid From", "Valid Until", "Tariff ID", "Is Active", "Created At"
    ])
    
    # Data
    for promo in promocodes:
        writer.writerow([
            promo.id,
            promo.code,
            promo.discount_percent,
            promo.discount_amount,
            promo.max_uses or "Unlimited",
            promo.used_count,
            promo.valid_from.isoformat() if promo.valid_from else "",
            promo.valid_until.isoformat() if promo.valid_until else "",
            promo.tariff_id or "All",
            promo.is_active,
            promo.created_at.isoformat()
        ])
    
    output.seek(0)
    
    filename = f"promocodes_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
