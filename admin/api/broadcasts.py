"""
API endpoints для рассылок.
"""

import json
import asyncio
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from admin.schemas.broadcast import (
    BroadcastCreate,
    BroadcastUpdate,
    BroadcastResponse,
    BroadcastListResponse,
    BroadcastCountResponse,
    BroadcastStatusResponse,
    QuickBroadcastRequest,
    QuickBroadcastResponse,
)
from bot.models import Broadcast
from bot.services.broadcast import (
    create_broadcast,
    get_broadcast,
    update_broadcast,
    delete_broadcast,
    start_broadcast,
    pause_broadcast,
    resume_broadcast,
    cancel_broadcast,
    get_broadcasts_list,
    count_broadcast_recipients,
    quick_broadcast,
    BroadcastNotFoundError,
    BroadcastInvalidStateError,
)
from bot.loader import bot

router = APIRouter(prefix="/broadcasts", tags=["broadcasts"])


def broadcast_to_response(broadcast: Broadcast) -> BroadcastResponse:
    """Конвертировать модель в ответ."""
    return BroadcastResponse(
        id=broadcast.id,
        message_text=broadcast.message_text,
        message_photo=broadcast.message_photo,
        buttons_json=broadcast.buttons_json,
        filter_type=broadcast.filter_type,
        filter_language=broadcast.filter_language,
        total_users=broadcast.total_users,
        sent_count=broadcast.sent_count,
        failed_count=broadcast.failed_count,
        status=broadcast.status,
        scheduled_at=broadcast.scheduled_at,
        started_at=broadcast.started_at,
        completed_at=broadcast.completed_at,
        created_at=broadcast.created_at,
        progress_percent=broadcast.progress_percent,
    )


@router.get("", response_model=BroadcastListResponse)
async def list_broadcasts(
    status: Literal["draft", "running", "paused", "completed", "cancelled"] | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """Получить список рассылок."""
    broadcasts = await get_broadcasts_list(session, status, limit, offset)
    
    # Общее количество
    stmt = select(func.count(Broadcast.id))
    if status:
        stmt = stmt.where(Broadcast.status == status)
    total = await session.scalar(stmt) or 0
    
    return BroadcastListResponse(
        items=[broadcast_to_response(b) for b in broadcasts],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=BroadcastResponse)
async def create_new_broadcast(
    data: BroadcastCreate,
    session: AsyncSession = Depends(get_session),
):
    """Создать новую рассылку."""
    # Конвертируем кнопки в JSON
    buttons_json = None
    if data.buttons:
        buttons_json = json.dumps([[btn.model_dump(exclude_none=True) for btn in row] for row in data.buttons])
    
    broadcast = await create_broadcast(
        session=session,
        message_text=data.message_text,
        message_photo=data.message_photo,
        buttons_json=buttons_json,
        filter_type=data.filter_type,
        filter_language=data.filter_language,
        scheduled_at=data.scheduled_at,
    )
    
    return broadcast_to_response(broadcast)


@router.get("/count", response_model=BroadcastCountResponse)
async def get_recipients_count(
    filter_type: str = Query("all", pattern=r"^(all|active|inactive|tariff_\d+)$"),
    filter_language: Literal["all", "ru", "en"] = "all",
    session: AsyncSession = Depends(get_session),
):
    """Получить количество получателей по фильтрам."""
    count = await count_broadcast_recipients(session, filter_type, filter_language)
    return BroadcastCountResponse(
        count=count,
        filter_type=filter_type,
        filter_language=filter_language,
    )


@router.get("/{broadcast_id}", response_model=BroadcastResponse)
async def get_broadcast_by_id(
    broadcast_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Получить рассылку по ID."""
    try:
        broadcast = await get_broadcast(session, broadcast_id)
        return broadcast_to_response(broadcast)
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")


@router.patch("/{broadcast_id}", response_model=BroadcastResponse)
async def update_broadcast_by_id(
    broadcast_id: int,
    data: BroadcastUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Обновить рассылку."""
    try:
        update_data = data.model_dump(exclude_none=True)
        
        # Конвертируем кнопки
        if "buttons" in update_data:
            if update_data["buttons"]:
                update_data["buttons_json"] = json.dumps([
                    [btn.model_dump(exclude_none=True) for btn in row] 
                    for row in update_data["buttons"]
                ])
            else:
                update_data["buttons_json"] = None
            del update_data["buttons"]
        
        broadcast = await update_broadcast(session, broadcast_id, **update_data)
        return broadcast_to_response(broadcast)
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    except BroadcastInvalidStateError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{broadcast_id}")
async def delete_broadcast_by_id(
    broadcast_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Удалить рассылку."""
    try:
        await delete_broadcast(session, broadcast_id)
        return {"message": "Broadcast deleted"}
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    except BroadcastInvalidStateError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{broadcast_id}/start", response_model=BroadcastStatusResponse)
async def start_broadcast_by_id(
    broadcast_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Запустить рассылку в фоне."""
    try:
        broadcast = await get_broadcast(session, broadcast_id)
        
        if broadcast.status not in ("draft", "paused"):
            raise HTTPException(status_code=400, detail=f"Cannot start broadcast in {broadcast.status} state")
        
        # Обновляем статус
        broadcast.status = "running"
        if not broadcast.started_at:
            from datetime import datetime
            broadcast.started_at = datetime.utcnow()
        await session.commit()
        
        # Запускаем в фоне
        async def run_broadcast():
            from admin.database import async_session_factory
            async with async_session_factory() as bg_session:
                await start_broadcast(bg_session, bot, broadcast_id)
        
        background_tasks.add_task(asyncio.create_task, run_broadcast())
        
        return BroadcastStatusResponse(
            id=broadcast.id,
            status=broadcast.status,
            sent_count=broadcast.sent_count,
            failed_count=broadcast.failed_count,
            total_users=broadcast.total_users,
            progress_percent=broadcast.progress_percent,
        )
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")


@router.post("/{broadcast_id}/pause", response_model=BroadcastStatusResponse)
async def pause_broadcast_by_id(
    broadcast_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Поставить рассылку на паузу."""
    try:
        broadcast = await pause_broadcast(session, broadcast_id)
        return BroadcastStatusResponse(
            id=broadcast.id,
            status=broadcast.status,
            sent_count=broadcast.sent_count,
            failed_count=broadcast.failed_count,
            total_users=broadcast.total_users,
            progress_percent=broadcast.progress_percent,
        )
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    except BroadcastInvalidStateError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{broadcast_id}/resume", response_model=BroadcastStatusResponse)
async def resume_broadcast_by_id(
    broadcast_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Возобновить рассылку."""
    try:
        broadcast = await get_broadcast(session, broadcast_id)
        
        if broadcast.status != "paused":
            raise HTTPException(status_code=400, detail="Can only resume paused broadcasts")
        
        # Обновляем статус
        broadcast.status = "running"
        await session.commit()
        
        # Запускаем в фоне
        async def run_broadcast():
            from admin.database import async_session_factory
            async with async_session_factory() as bg_session:
                await start_broadcast(bg_session, bot, broadcast_id)
        
        background_tasks.add_task(asyncio.create_task, run_broadcast())
        
        return BroadcastStatusResponse(
            id=broadcast.id,
            status=broadcast.status,
            sent_count=broadcast.sent_count,
            failed_count=broadcast.failed_count,
            total_users=broadcast.total_users,
            progress_percent=broadcast.progress_percent,
        )
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")


@router.post("/{broadcast_id}/cancel", response_model=BroadcastStatusResponse)
async def cancel_broadcast_by_id(
    broadcast_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Отменить рассылку."""
    try:
        broadcast = await cancel_broadcast(session, broadcast_id)
        return BroadcastStatusResponse(
            id=broadcast.id,
            status=broadcast.status,
            sent_count=broadcast.sent_count,
            failed_count=broadcast.failed_count,
            total_users=broadcast.total_users,
            progress_percent=broadcast.progress_percent,
        )
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    except BroadcastInvalidStateError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{broadcast_id}/status", response_model=BroadcastStatusResponse)
async def get_broadcast_status(
    broadcast_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Получить статус рассылки."""
    try:
        broadcast = await get_broadcast(session, broadcast_id)
        return BroadcastStatusResponse(
            id=broadcast.id,
            status=broadcast.status,
            sent_count=broadcast.sent_count,
            failed_count=broadcast.failed_count,
            total_users=broadcast.total_users,
            progress_percent=broadcast.progress_percent,
        )
    except BroadcastNotFoundError:
        raise HTTPException(status_code=404, detail="Broadcast not found")


@router.post("/quick", response_model=QuickBroadcastResponse)
async def send_quick_broadcast(
    data: QuickBroadcastRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Быстрая рассылка (синхронная).
    
    Отправляет сразу, не создаёт запись в БД.
    Используйте для небольших рассылок.
    """
    result = await quick_broadcast(
        session=session,
        bot=bot,
        message_text=data.message_text,
        filter_type=data.filter_type,
        filter_language=data.filter_language,
    )
    
    return QuickBroadcastResponse(**result)
