"""Payments API endpoints."""

from math import ceil
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from admin.schemas.payment import (
    ManualPaymentCreate,
    ManualConfirm,
    PaymentResponse,
    PaymentListResponse,
    PaymentStats,
    RevenueByDay,
    UserShort,
    TariffShort,
)
from bot.models import Payment, User, Tariff, Subscription

router = APIRouter(prefix="/payments", tags=["Payments"])


async def _build_payment_response(
    session: AsyncSession, 
    payment: Payment
) -> PaymentResponse:
    """Build payment response."""
    # Get user
    user_result = await session.execute(
        select(User).where(User.id == payment.user_id)
    )
    user = user_result.scalar_one()
    
    # Get tariff if exists
    tariff = None
    if payment.tariff_id:
        tariff_result = await session.execute(
            select(Tariff).where(Tariff.id == payment.tariff_id)
        )
        tariff_obj = tariff_result.scalar_one_or_none()
        if tariff_obj:
            tariff = TariffShort(
                id=tariff_obj.id,
                name_ru=tariff_obj.name_ru,
                name_en=tariff_obj.name_en,
                price=tariff_obj.price
            )
    
    return PaymentResponse(
        id=payment.id,
        user=UserShort(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name
        ),
        tariff=tariff,
        subscription_id=payment.subscription_id,
        invoice_id=payment.invoice_id,
        amount=payment.amount,
        original_amount=payment.original_amount,
        promocode_id=payment.promocode_id,
        status=payment.status,
        payment_method=payment.payment_method,
        confirmed_by=payment.confirmed_by,
        paid_at=payment.paid_at,
        created_at=payment.created_at
    )


@router.get("", response_model=PaymentListResponse)
async def get_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    tariff_id: int | None = None,
    status: str | None = None,
    payment_method: str | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Get list of payments with pagination."""
    query = select(Payment)
    count_query = select(func.count(Payment.id))
    
    # Filters
    if user_id is not None:
        query = query.where(Payment.user_id == user_id)
        count_query = count_query.where(Payment.user_id == user_id)
    
    if tariff_id is not None:
        query = query.where(Payment.tariff_id == tariff_id)
        count_query = count_query.where(Payment.tariff_id == tariff_id)
    
    if status:
        query = query.where(Payment.status == status)
        count_query = count_query.where(Payment.status == status)
    
    if payment_method:
        query = query.where(Payment.payment_method == payment_method)
        count_query = count_query.where(Payment.payment_method == payment_method)
    
    # Count total
    total = await session.scalar(count_query)
    pages = ceil(total / per_page) if total else 1
    
    # Get items
    query = query.order_by(Payment.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await session.execute(query)
    payments = result.scalars().all()
    
    items = [await _build_payment_response(session, p) for p in payments]
    
    return PaymentListResponse(
        items=items,
        total=total or 0,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/stats", response_model=PaymentStats)
async def get_payment_stats(session: AsyncSession = Depends(get_session)):
    """Get payment statistics."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total count
    total_count = await session.scalar(select(func.count(Payment.id)))
    
    # Paid count
    paid_count = await session.scalar(
        select(func.count(Payment.id)).where(Payment.status == "paid")
    )
    
    # Pending count
    pending_count = await session.scalar(
        select(func.count(Payment.id)).where(Payment.status == "pending")
    )
    
    # Total amount
    total_amount = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid"
        )
    )
    
    # Today amount
    today_amount = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= today_start
        )
    )
    
    # Month amount
    month_amount = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= month_start
        )
    )
    
    return PaymentStats(
        total_count=total_count or 0,
        paid_count=paid_count or 0,
        pending_count=pending_count or 0,
        total_amount=float(total_amount or 0),
        today_amount=float(today_amount or 0),
        month_amount=float(month_amount or 0)
    )


@router.get("/revenue", response_model=list[RevenueByDay])
async def get_revenue_by_day(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session)
):
    """Get revenue by day for chart."""
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)
    
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
    revenue_data = []
    current = start_date
    while current <= now:
        date_str = current.strftime("%Y-%m-%d")
        if date_str in data:
            revenue_data.append(RevenueByDay(
                date=date_str,
                amount=data[date_str]["amount"],
                count=data[date_str]["count"]
            ))
        else:
            revenue_data.append(RevenueByDay(
                date=date_str,
                amount=0,
                count=0
            ))
        current += timedelta(days=1)
    
    return revenue_data


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get payment by ID."""
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return await _build_payment_response(session, payment)


@router.post("/manual", response_model=PaymentResponse)
async def create_manual_payment(
    data: ManualPaymentCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a manual payment and subscription."""
    # Check user exists
    user_result = await session.execute(
        select(User).where(User.id == data.user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check tariff exists
    tariff_result = await session.execute(
        select(Tariff).where(Tariff.id == data.tariff_id)
    )
    tariff = tariff_result.scalar_one_or_none()
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    
    now = datetime.utcnow()
    
    # Create subscription
    expires_at = None if tariff.duration_days == 0 else now + timedelta(days=tariff.duration_days)
    
    subscription = Subscription(
        user_id=data.user_id,
        tariff_id=data.tariff_id,
        is_trial=False,
        starts_at=now,
        expires_at=expires_at,
        is_active=True,
        granted_by=data.confirmed_by
    )
    session.add(subscription)
    await session.flush()
    
    # Create payment
    payment = Payment(
        user_id=data.user_id,
        tariff_id=data.tariff_id,
        subscription_id=subscription.id,
        amount=data.amount,
        original_amount=tariff.price,
        status="paid",
        payment_method="manual",
        confirmed_by=data.confirmed_by,
        paid_at=now
    )
    session.add(payment)
    
    await session.commit()
    await session.refresh(payment)
    
    return await _build_payment_response(session, payment)


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: int,
    data: ManualConfirm,
    session: AsyncSession = Depends(get_session)
):
    """Manually confirm a pending payment."""
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status != "pending":
        raise HTTPException(status_code=400, detail="Payment is not pending")
    
    now = datetime.utcnow()
    
    # Get tariff for subscription
    tariff_result = await session.execute(
        select(Tariff).where(Tariff.id == payment.tariff_id)
    )
    tariff = tariff_result.scalar_one_or_none()
    
    if tariff:
        # Create subscription
        expires_at = None if tariff.duration_days == 0 else now + timedelta(days=tariff.duration_days)
        
        subscription = Subscription(
            user_id=payment.user_id,
            tariff_id=payment.tariff_id,
            is_trial=False,
            starts_at=now,
            expires_at=expires_at,
            is_active=True,
            granted_by=data.confirmed_by
        )
        session.add(subscription)
        await session.flush()
        
        payment.subscription_id = subscription.id
    
    # Update payment
    payment.status = "paid"
    payment.payment_method = "manual"
    payment.confirmed_by = data.confirmed_by
    payment.paid_at = now
    
    await session.commit()
    await session.refresh(payment)
    
    return await _build_payment_response(session, payment)


@router.post("/{payment_id}/cancel")
async def cancel_payment(
    payment_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Cancel a pending payment."""
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status != "pending":
        raise HTTPException(status_code=400, detail="Payment is not pending")
    
    payment.status = "cancelled"
    await session.commit()
    
    return {"status": "ok", "message": "Payment cancelled"}


@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a payment."""
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    await session.delete(payment)
    await session.commit()
    
    return {"status": "ok", "message": "Payment deleted"}
