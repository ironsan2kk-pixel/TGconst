"""FAQ API endpoints."""

from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from admin.schemas.faq import (
    FAQItemCreate,
    FAQItemUpdate,
    FAQItemResponse,
    FAQItemListResponse,
    FAQStats,
    CategoryShort,
)
from bot.models import FAQItem, MenuItem

router = APIRouter(prefix="/faq", tags=["FAQ"])


async def _build_faq_response(
    session: AsyncSession, 
    faq: FAQItem
) -> FAQItemResponse:
    """Build FAQ response."""
    # Get category if exists
    category = None
    if faq.category_id:
        cat_result = await session.execute(
            select(MenuItem).where(MenuItem.id == faq.category_id)
        )
        cat_obj = cat_result.scalar_one_or_none()
        if cat_obj:
            category = CategoryShort(
                id=cat_obj.id,
                text_ru=cat_obj.text_ru,
                text_en=cat_obj.text_en
            )
    
    return FAQItemResponse(
        id=faq.id,
        question_ru=faq.question_ru,
        question_en=faq.question_en,
        answer_ru=faq.answer_ru,
        answer_en=faq.answer_en,
        category_id=faq.category_id,
        category=category,
        sort_order=faq.sort_order,
        is_active=faq.is_active,
        created_at=faq.created_at
    )


@router.get("", response_model=FAQItemListResponse)
async def get_faq_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category_id: int | None = None,
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Get list of FAQ items with pagination."""
    query = select(FAQItem)
    count_query = select(func.count(FAQItem.id))
    
    # Search
    if search:
        query = query.where(
            (FAQItem.question_ru.ilike(f"%{search}%")) |
            (FAQItem.question_en.ilike(f"%{search}%")) |
            (FAQItem.answer_ru.ilike(f"%{search}%")) |
            (FAQItem.answer_en.ilike(f"%{search}%"))
        )
        count_query = count_query.where(
            (FAQItem.question_ru.ilike(f"%{search}%")) |
            (FAQItem.question_en.ilike(f"%{search}%")) |
            (FAQItem.answer_ru.ilike(f"%{search}%")) |
            (FAQItem.answer_en.ilike(f"%{search}%"))
        )
    
    # Filters
    if category_id is not None:
        query = query.where(FAQItem.category_id == category_id)
        count_query = count_query.where(FAQItem.category_id == category_id)
    
    if is_active is not None:
        query = query.where(FAQItem.is_active == is_active)
        count_query = count_query.where(FAQItem.is_active == is_active)
    
    # Count total
    total = await session.scalar(count_query)
    pages = ceil(total / per_page) if total else 1
    
    # Get items
    query = query.order_by(FAQItem.sort_order, FAQItem.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await session.execute(query)
    faqs = result.scalars().all()
    
    items = [await _build_faq_response(session, f) for f in faqs]
    
    return FAQItemListResponse(
        items=items,
        total=total or 0,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/stats", response_model=FAQStats)
async def get_faq_stats(session: AsyncSession = Depends(get_session)):
    """Get FAQ statistics."""
    # Total
    total = await session.scalar(select(func.count(FAQItem.id)))
    
    # Active
    active = await session.scalar(
        select(func.count(FAQItem.id)).where(FAQItem.is_active == True)
    )
    
    # By category
    result = await session.execute(
        select(
            FAQItem.category_id,
            func.count(FAQItem.id).label("count")
        ).group_by(FAQItem.category_id)
    )
    
    by_category = {}
    for row in result:
        cat_id = row.category_id or 0
        if cat_id:
            # Get category name
            cat_result = await session.execute(
                select(MenuItem).where(MenuItem.id == cat_id)
            )
            cat = cat_result.scalar_one_or_none()
            cat_name = cat.text_ru if cat else f"Category {cat_id}"
        else:
            cat_name = "Uncategorized"
        by_category[cat_name] = row.count
    
    return FAQStats(
        total=total or 0,
        active=active or 0,
        by_category=by_category
    )


@router.get("/categories")
async def get_faq_categories(session: AsyncSession = Depends(get_session)):
    """Get available FAQ categories (menu items of type 'section')."""
    result = await session.execute(
        select(MenuItem).where(
            MenuItem.type == "section"
        ).order_by(MenuItem.sort_order)
    )
    items = result.scalars().all()
    
    return {
        "categories": [
            {
                "id": item.id,
                "text_ru": item.text_ru,
                "text_en": item.text_en
            }
            for item in items
        ]
    }


@router.get("/{faq_id}", response_model=FAQItemResponse)
async def get_faq_item(
    faq_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get FAQ item by ID."""
    result = await session.execute(
        select(FAQItem).where(FAQItem.id == faq_id)
    )
    faq = result.scalar_one_or_none()
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ item not found")
    
    return await _build_faq_response(session, faq)


@router.post("", response_model=FAQItemResponse)
async def create_faq_item(
    data: FAQItemCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new FAQ item."""
    # Validate category exists if provided
    if data.category_id:
        cat_result = await session.execute(
            select(MenuItem).where(MenuItem.id == data.category_id)
        )
        if not cat_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Category not found")
    
    faq = FAQItem(
        question_ru=data.question_ru,
        question_en=data.question_en,
        answer_ru=data.answer_ru,
        answer_en=data.answer_en,
        category_id=data.category_id,
        sort_order=data.sort_order,
        is_active=data.is_active
    )
    session.add(faq)
    await session.commit()
    await session.refresh(faq)
    
    return await _build_faq_response(session, faq)


@router.patch("/{faq_id}", response_model=FAQItemResponse)
async def update_faq_item(
    faq_id: int,
    data: FAQItemUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a FAQ item."""
    result = await session.execute(
        select(FAQItem).where(FAQItem.id == faq_id)
    )
    faq = result.scalar_one_or_none()
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ item not found")
    
    # Validate category exists if changing
    if data.category_id is not None and data.category_id != faq.category_id:
        if data.category_id:
            cat_result = await session.execute(
                select(MenuItem).where(MenuItem.id == data.category_id)
            )
            if not cat_result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)
    
    await session.commit()
    await session.refresh(faq)
    
    return await _build_faq_response(session, faq)


@router.delete("/{faq_id}")
async def delete_faq_item(
    faq_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a FAQ item."""
    result = await session.execute(
        select(FAQItem).where(FAQItem.id == faq_id)
    )
    faq = result.scalar_one_or_none()
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ item not found")
    
    await session.delete(faq)
    await session.commit()
    
    return {"status": "ok", "message": "FAQ item deleted"}
