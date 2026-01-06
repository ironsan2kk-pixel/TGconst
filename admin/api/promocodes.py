"""Promocodes API endpoints."""

from math import ceil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from admin.schemas.promocode import (
    PromocodeCreate,
    PromocodeUpdate,
    PromocodeResponse,
    PromocodeListResponse,
    PromocodeStats,
    TariffShort,
)
from bot.models import Promocode, Tariff, Payment

router = APIRouter(prefix="/promocodes", tags=["Promocodes"])


async def _build_promocode_response(
    session: AsyncSession, 
    promo: Promocode
) -> PromocodeResponse:
    """Build promocode response."""
    # Get tariff if exists
    tariff = None
    if promo.tariff_id:
        tariff_result = await session.execute(
            select(Tariff).where(Tariff.id == promo.tariff_id)
        )
        tariff_obj = tariff_result.scalar_one_or_none()
        if tariff_obj:
            tariff = TariffShort(
                id=tariff_obj.id,
                name_ru=tariff_obj.name_ru,
                name_en=tariff_obj.name_en
            )
    
    return PromocodeResponse(
        id=promo.id,
        code=promo.code,
        discount_percent=promo.discount_percent,
        discount_amount=promo.discount_amount,
        max_uses=promo.max_uses,
        used_count=promo.used_count,
        valid_from=promo.valid_from,
        valid_until=promo.valid_until,
        tariff=tariff,
        is_active=promo.is_active,
        is_valid=promo.is_valid,
        created_at=promo.created_at
    )


@router.get("", response_model=PromocodeListResponse)
async def get_promocodes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Get list of promocodes with pagination."""
    query = select(Promocode)
    count_query = select(func.count(Promocode.id))
    
    # Search
    if search:
        query = query.where(Promocode.code.ilike(f"%{search}%"))
        count_query = count_query.where(Promocode.code.ilike(f"%{search}%"))
    
    # Filters
    if is_active is not None:
        query = query.where(Promocode.is_active == is_active)
        count_query = count_query.where(Promocode.is_active == is_active)
    
    # Count total
    total = await session.scalar(count_query)
    pages = ceil(total / per_page) if total else 1
    
    # Get items
    query = query.order_by(Promocode.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await session.execute(query)
    promocodes = result.scalars().all()
    
    items = [await _build_promocode_response(session, p) for p in promocodes]
    
    return PromocodeListResponse(
        items=items,
        total=total or 0,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/stats", response_model=PromocodeStats)
async def get_promocode_stats(session: AsyncSession = Depends(get_session)):
    """Get promocode statistics."""
    # Total
    total = await session.scalar(select(func.count(Promocode.id)))
    
    # Active
    active = await session.scalar(
        select(func.count(Promocode.id)).where(Promocode.is_active == True)
    )
    
    # Total uses
    total_uses = await session.scalar(
        select(func.coalesce(func.sum(Promocode.used_count), 0))
    )
    
    # Total discount given (from payments with promocode)
    result = await session.execute(
        select(
            func.coalesce(
                func.sum(Payment.original_amount - Payment.amount), 
                0
            )
        ).where(
            Payment.promocode_id.isnot(None),
            Payment.status == "paid"
        )
    )
    total_discount = result.scalar() or 0
    
    return PromocodeStats(
        total=total or 0,
        active=active or 0,
        total_uses=int(total_uses or 0),
        total_discount_given=float(total_discount)
    )


@router.get("/check/{code}")
async def check_promocode(
    code: str,
    tariff_id: int | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Check if promocode is valid."""
    result = await session.execute(
        select(Promocode).where(Promocode.code == code.upper())
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        return {"valid": False, "error": "Promocode not found"}
    
    if not promo.is_valid:
        return {"valid": False, "error": "Promocode is not valid"}
    
    if promo.tariff_id and tariff_id and promo.tariff_id != tariff_id:
        return {"valid": False, "error": "Promocode not valid for this tariff"}
    
    return {
        "valid": True,
        "discount_percent": promo.discount_percent,
        "discount_amount": promo.discount_amount
    }


@router.get("/{promocode_id}", response_model=PromocodeResponse)
async def get_promocode(
    promocode_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get promocode by ID."""
    result = await session.execute(
        select(Promocode).where(Promocode.id == promocode_id)
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promocode not found")
    
    return await _build_promocode_response(session, promo)


@router.post("", response_model=PromocodeResponse)
async def create_promocode(
    data: PromocodeCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new promocode."""
    # Check for duplicate code
    existing = await session.scalar(
        select(Promocode).where(Promocode.code == data.code.upper())
    )
    if existing:
        raise HTTPException(status_code=400, detail="Promocode already exists")
    
    promo = Promocode(
        code=data.code.upper(),
        discount_percent=data.discount_percent,
        discount_amount=data.discount_amount,
        max_uses=data.max_uses,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        tariff_id=data.tariff_id,
        is_active=data.is_active
    )
    session.add(promo)
    await session.commit()
    await session.refresh(promo)
    
    return await _build_promocode_response(session, promo)


@router.patch("/{promocode_id}", response_model=PromocodeResponse)
async def update_promocode(
    promocode_id: int,
    data: PromocodeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a promocode."""
    result = await session.execute(
        select(Promocode).where(Promocode.id == promocode_id)
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promocode not found")
    
    # Check for duplicate code if updating
    if data.code and data.code.upper() != promo.code:
        existing = await session.scalar(
            select(Promocode).where(Promocode.code == data.code.upper())
        )
        if existing:
            raise HTTPException(status_code=400, detail="Promocode already exists")
    
    update_data = data.model_dump(exclude_unset=True)
    if "code" in update_data:
        update_data["code"] = update_data["code"].upper()
    
    for field, value in update_data.items():
        setattr(promo, field, value)
    
    await session.commit()
    await session.refresh(promo)
    
    return await _build_promocode_response(session, promo)


@router.delete("/{promocode_id}")
async def delete_promocode(
    promocode_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a promocode."""
    result = await session.execute(
        select(Promocode).where(Promocode.id == promocode_id)
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promocode not found")
    
    await session.delete(promo)
    await session.commit()
    
    return {"status": "ok", "message": "Promocode deleted"}
