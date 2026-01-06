"""Dashboard API endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from bot.models import User, Subscription, Payment, Tariff

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_session)):
    """Get dashboard statistics."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total users
    total_users = await session.scalar(select(func.count(User.id)))
    
    # Active subscriptions
    active_subs = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.is_active == True,
            (Subscription.expires_at == None) | (Subscription.expires_at > now)
        )
    )
    
    # Revenue today
    today_revenue = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= today_start
        )
    )
    
    # Revenue this month
    month_revenue = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= month_start
        )
    )
    
    # New users today
    new_users_today = await session.scalar(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )
    
    # New users this month
    new_users_month = await session.scalar(
        select(func.count(User.id)).where(User.created_at >= month_start)
    )
    
    # Pending payments
    pending_payments = await session.scalar(
        select(func.count(Payment.id)).where(Payment.status == "pending")
    )
    
    return {
        "users": {
            "total": total_users or 0,
            "today": new_users_today or 0,
            "month": new_users_month or 0,
        },
        "subscriptions": {
            "active": active_subs or 0,
        },
        "revenue": {
            "today": float(today_revenue or 0),
            "month": float(month_revenue or 0),
        },
        "payments": {
            "pending": pending_payments or 0,
        }
    }


@router.get("/chart/revenue")
async def get_revenue_chart(
    days: int = 30,
    session: AsyncSession = Depends(get_session)
):
    """Get revenue chart data for last N days."""
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)
    
    # Get daily revenue
    result = await session.execute(
        select(
            func.date(Payment.paid_at).label("date"),
            func.sum(Payment.amount).label("amount"),
            func.count(Payment.id).label("count")
        ).where(
            Payment.status == "paid",
            Payment.paid_at >= start_date
        ).group_by(func.date(Payment.paid_at)).order_by(func.date(Payment.paid_at))
    )
    
    data = {}
    for row in result:
        data[str(row.date)] = {
            "amount": float(row.amount or 0),
            "count": row.count or 0
        }
    
    # Fill missing days
    chart_data = []
    current = start_date
    while current <= now:
        date_str = current.strftime("%Y-%m-%d")
        if date_str in data:
            chart_data.append({
                "date": date_str,
                "amount": data[date_str]["amount"],
                "count": data[date_str]["count"]
            })
        else:
            chart_data.append({
                "date": date_str,
                "amount": 0,
                "count": 0
            })
        current += timedelta(days=1)
    
    return {"data": chart_data}


@router.get("/chart/users")
async def get_users_chart(
    days: int = 30,
    session: AsyncSession = Depends(get_session)
):
    """Get new users chart data for last N days."""
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)
    
    # Get daily new users
    result = await session.execute(
        select(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count")
        ).where(
            User.created_at >= start_date
        ).group_by(func.date(User.created_at)).order_by(func.date(User.created_at))
    )
    
    data = {}
    for row in result:
        data[str(row.date)] = row.count or 0
    
    # Fill missing days
    chart_data = []
    current = start_date
    while current <= now:
        date_str = current.strftime("%Y-%m-%d")
        chart_data.append({
            "date": date_str,
            "count": data.get(date_str, 0)
        })
        current += timedelta(days=1)
    
    return {"data": chart_data}


@router.get("/recent")
async def get_recent_activity(
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    """Get recent activity (registrations and purchases)."""
    # Recent users
    result = await session.execute(
        select(User).order_by(User.created_at.desc()).limit(limit)
    )
    recent_users = result.scalars().all()
    
    # Recent payments
    result = await session.execute(
        select(Payment).where(
            Payment.status == "paid"
        ).order_by(Payment.paid_at.desc()).limit(limit)
    )
    recent_payments = result.scalars().all()
    
    return {
        "users": [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "first_name": u.first_name,
                "created_at": u.created_at.isoformat()
            }
            for u in recent_users
        ],
        "payments": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "amount": p.amount,
                "status": p.status,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None
            }
            for p in recent_payments
        ]
    }


@router.get("/conversion")
async def get_conversion_stats(session: AsyncSession = Depends(get_session)):
    """Get conversion statistics."""
    # Total users who ever subscribed
    users_with_subs = await session.scalar(
        select(func.count(func.distinct(Subscription.user_id)))
    )
    
    # Total users
    total_users = await session.scalar(select(func.count(User.id)))
    
    # Users who paid
    users_with_payments = await session.scalar(
        select(func.count(func.distinct(Payment.user_id))).where(
            Payment.status == "paid"
        )
    )
    
    conversion_rate = 0
    if total_users and total_users > 0:
        conversion_rate = round((users_with_payments or 0) / total_users * 100, 2)
    
    return {
        "total_users": total_users or 0,
        "users_with_subscriptions": users_with_subs or 0,
        "users_with_payments": users_with_payments or 0,
        "conversion_rate": conversion_rate
    }
