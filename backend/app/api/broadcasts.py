"""
API эндпоинты для управления рассылками
"""
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, status, Path, Query, BackgroundTasks
from sqlalchemy import select, func

from ..models.bot_db import Broadcast, User
from ..schemas.broadcast import (
    BroadcastCreate,
    BroadcastUpdate,
    BroadcastResponse,
    BroadcastListResponse,
    BroadcastStartResponse,
    BroadcastCancelResponse,
    BroadcastStatsResponse
)
from .deps import BotDbSession, CurrentAdmin

router = APIRouter()

# Глобальный словарь для отслеживания активных рассылок
# Ключ: broadcast_id, Значение: {"cancelled": bool}
_active_broadcasts: dict[int, dict] = {}


def broadcast_to_response(broadcast: Broadcast) -> BroadcastResponse:
    """Преобразование модели в ответ"""
    return BroadcastResponse(
        id=broadcast.id,
        message_text=broadcast.message_text,
        message_photo=broadcast.message_photo,
        total_users=broadcast.total_users,
        sent_count=broadcast.sent_count,
        failed_count=broadcast.failed_count,
        status=broadcast.status,
        progress_percent=broadcast.progress_percent,
        started_at=broadcast.started_at,
        completed_at=broadcast.completed_at,
        created_at=broadcast.created_at
    )


async def get_broadcast_or_404(bot_db, broadcast_id: int) -> Broadcast:
    """Вспомогательная функция для получения рассылки или 404"""
    result = await bot_db.execute(
        select(Broadcast).where(Broadcast.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()
    
    if broadcast is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рассылка не найдена"
        )
    
    return broadcast


@router.get(
    "",
    response_model=BroadcastListResponse,
    summary="Список рассылок",
    description="Получение списка всех рассылок бота"
)
async def get_broadcasts(
    bot_db: BotDbSession,
    current_admin: CurrentAdmin,
    status_filter: Annotated[Optional[str], Query(
        alias="status",
        description="Фильтр по статусу: pending, running, completed, cancelled"
    )] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Лимит записей")] = 50,
    offset: Annotated[int, Query(ge=0, description="Смещение")] = 0
) -> BroadcastListResponse:
    """
    Получить список всех рассылок.
    
    Можно фильтровать по статусу:
    - pending: ожидает запуска
    - running: выполняется
    - completed: завершена
    - cancelled: отменена
    """
    # Базовый запрос
    query = select(Broadcast)
    
    # Фильтр по статусу
    if status_filter:
        valid_statuses = ["pending", "running", "completed", "cancelled"]
        if status_filter not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимый статус. Допустимые: {', '.join(valid_statuses)}"
            )
        query = query.where(Broadcast.status == status_filter)
    
    # Сортировка и пагинация
    query = query.order_by(Broadcast.created_at.desc()).offset(offset).limit(limit)
    
    # Выполняем запрос
    result = await bot_db.execute(query)
    broadcasts = result.scalars().all()
    
    # Считаем статистику (без фильтра)
    stats_result = await bot_db.execute(select(Broadcast))
    all_broadcasts = stats_result.scalars().all()
    
    total = len(all_broadcasts)
    pending_count = sum(1 for b in all_broadcasts if b.status == "pending")
    running_count = sum(1 for b in all_broadcasts if b.status == "running")
    completed_count = sum(1 for b in all_broadcasts if b.status == "completed")
    
    items = [broadcast_to_response(b) for b in broadcasts]
    
    return BroadcastListResponse(
        total=total,
        pending_count=pending_count,
        running_count=running_count,
        completed_count=completed_count,
        items=items
    )


@router.post(
    "",
    response_model=BroadcastResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать рассылку",
    description="Создание новой рассылки (без запуска)"
)
async def create_broadcast(
    data: BroadcastCreate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> BroadcastResponse:
    """
    Создать новую рассылку.
    
    Рассылка создаётся в статусе 'pending'.
    Для запуска используйте эндпоинт POST /{id}/start.
    """
    # Считаем количество активных пользователей (не заблокировавших бота)
    result = await bot_db.execute(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    total_users = result.scalar() or 0
    
    # Создаём рассылку
    broadcast = Broadcast(
        message_text=data.message_text,
        message_photo=data.message_photo,
        total_users=total_users,
        sent_count=0,
        failed_count=0,
        status="pending"
    )
    
    bot_db.add(broadcast)
    await bot_db.commit()
    await bot_db.refresh(broadcast)
    
    return broadcast_to_response(broadcast)


@router.get(
    "/{broadcast_id}",
    response_model=BroadcastResponse,
    summary="Получить рассылку",
    description="Получение информации о конкретной рассылке"
)
async def get_broadcast(
    broadcast_id: Annotated[int, Path(description="ID рассылки в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> BroadcastResponse:
    """Получить рассылку по ID"""
    broadcast = await get_broadcast_or_404(bot_db, broadcast_id)
    return broadcast_to_response(broadcast)


@router.put(
    "/{broadcast_id}",
    response_model=BroadcastResponse,
    summary="Обновить рассылку",
    description="Обновление текста рассылки (только для pending)"
)
async def update_broadcast(
    broadcast_id: Annotated[int, Path(description="ID рассылки в БД")],
    data: BroadcastUpdate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> BroadcastResponse:
    """
    Обновить рассылку.
    
    Можно обновлять только рассылки в статусе 'pending'.
    """
    broadcast = await get_broadcast_or_404(bot_db, broadcast_id)
    
    if broadcast.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно редактировать рассылку в статусе '{broadcast.status}'. Редактирование доступно только для 'pending'."
        )
    
    # Обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(broadcast, field, value)
    
    # Обновляем количество пользователей (могло измениться)
    result = await bot_db.execute(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    broadcast.total_users = result.scalar() or 0
    
    await bot_db.commit()
    await bot_db.refresh(broadcast)
    
    return broadcast_to_response(broadcast)


@router.delete(
    "/{broadcast_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить рассылку",
    description="Удаление рассылки"
)
async def delete_broadcast(
    broadcast_id: Annotated[int, Path(description="ID рассылки в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> None:
    """
    Удалить рассылку.
    
    Нельзя удалить рассылку в статусе 'running'.
    """
    broadcast = await get_broadcast_or_404(bot_db, broadcast_id)
    
    if broadcast.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно удалить выполняющуюся рассылку. Сначала отмените её."
        )
    
    await bot_db.delete(broadcast)
    await bot_db.commit()


@router.post(
    "/{broadcast_id}/start",
    response_model=BroadcastStartResponse,
    summary="Запустить рассылку",
    description="Запуск рассылки сообщений"
)
async def start_broadcast(
    broadcast_id: Annotated[int, Path(description="ID рассылки в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin,
    background_tasks: BackgroundTasks
) -> BroadcastStartResponse:
    """
    Запустить рассылку.
    
    Рассылка выполняется в фоновом режиме.
    Можно запустить только рассылку в статусе 'pending'.
    
    После запуска статус меняется на 'running'.
    По завершении — на 'completed'.
    """
    broadcast = await get_broadcast_or_404(bot_db, broadcast_id)
    
    if broadcast.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно запустить рассылку в статусе '{broadcast.status}'. Запуск доступен только для 'pending'."
        )
    
    # Актуализируем количество получателей
    result = await bot_db.execute(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    total_users = result.scalar() or 0
    
    if total_users == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет пользователей для рассылки (все заблокировали бота или база пуста)"
        )
    
    # Обновляем статус
    broadcast.status = "running"
    broadcast.total_users = total_users
    broadcast.started_at = datetime.utcnow()
    
    await bot_db.commit()
    await bot_db.refresh(broadcast)
    
    # Регистрируем рассылку как активную
    _active_broadcasts[broadcast_id] = {"cancelled": False}
    
    # Фоновая задача для рассылки будет реализована в bot_template
    # Здесь мы просто помечаем рассылку как запущенную
    # Реальная отправка происходит в сервисе broadcast_worker
    
    return BroadcastStartResponse(
        success=True,
        message=f"Рассылка запущена. Всего получателей: {total_users}",
        broadcast=broadcast_to_response(broadcast)
    )


@router.post(
    "/{broadcast_id}/cancel",
    response_model=BroadcastCancelResponse,
    summary="Отменить рассылку",
    description="Отмена выполняющейся рассылки"
)
async def cancel_broadcast(
    broadcast_id: Annotated[int, Path(description="ID рассылки в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> BroadcastCancelResponse:
    """
    Отменить рассылку.
    
    Можно отменить рассылку в статусе 'pending' или 'running'.
    Уже отправленные сообщения не будут отозваны.
    """
    broadcast = await get_broadcast_or_404(bot_db, broadcast_id)
    
    if broadcast.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно отменить рассылку в статусе '{broadcast.status}'."
        )
    
    # Помечаем рассылку как отменённую
    if broadcast_id in _active_broadcasts:
        _active_broadcasts[broadcast_id]["cancelled"] = True
    
    # Обновляем статус
    was_running = broadcast.status == "running"
    broadcast.status = "cancelled"
    broadcast.completed_at = datetime.utcnow()
    
    await bot_db.commit()
    await bot_db.refresh(broadcast)
    
    # Удаляем из активных
    _active_broadcasts.pop(broadcast_id, None)
    
    if was_running:
        message = f"Рассылка отменена. Отправлено {broadcast.sent_count} из {broadcast.total_users} сообщений."
    else:
        message = "Рассылка отменена до запуска."
    
    return BroadcastCancelResponse(
        success=True,
        message=message,
        broadcast=broadcast_to_response(broadcast)
    )


@router.post(
    "/{broadcast_id}/restart",
    response_model=BroadcastStartResponse,
    summary="Перезапустить рассылку",
    description="Создание копии и запуск рассылки заново"
)
async def restart_broadcast(
    broadcast_id: Annotated[int, Path(description="ID рассылки в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin,
    background_tasks: BackgroundTasks
) -> BroadcastStartResponse:
    """
    Перезапустить рассылку.
    
    Создаёт копию рассылки и запускает её заново.
    Доступно для рассылок в статусе 'completed' или 'cancelled'.
    """
    broadcast = await get_broadcast_or_404(bot_db, broadcast_id)
    
    if broadcast.status not in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Перезапуск доступен только для завершённых или отменённых рассылок."
        )
    
    # Считаем получателей
    result = await bot_db.execute(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    total_users = result.scalar() or 0
    
    if total_users == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет пользователей для рассылки"
        )
    
    # Создаём новую рассылку
    new_broadcast = Broadcast(
        message_text=broadcast.message_text,
        message_photo=broadcast.message_photo,
        total_users=total_users,
        sent_count=0,
        failed_count=0,
        status="running",
        started_at=datetime.utcnow()
    )
    
    bot_db.add(new_broadcast)
    await bot_db.commit()
    await bot_db.refresh(new_broadcast)
    
    # Регистрируем как активную
    _active_broadcasts[new_broadcast.id] = {"cancelled": False}
    
    return BroadcastStartResponse(
        success=True,
        message=f"Рассылка перезапущена (новый ID: {new_broadcast.id}). Всего получателей: {total_users}",
        broadcast=broadcast_to_response(new_broadcast)
    )


@router.get(
    "/stats/summary",
    response_model=BroadcastStatsResponse,
    summary="Статистика рассылок",
    description="Общая статистика по рассылкам"
)
async def get_broadcasts_stats(
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> BroadcastStatsResponse:
    """
    Получить общую статистику по рассылкам.
    """
    # Получаем все рассылки
    result = await bot_db.execute(select(Broadcast))
    broadcasts = result.scalars().all()
    
    total_broadcasts = len(broadcasts)
    total_sent = sum(b.sent_count for b in broadcasts)
    total_failed = sum(b.failed_count for b in broadcasts)
    pending = sum(1 for b in broadcasts if b.status == "pending")
    running = sum(1 for b in broadcasts if b.status == "running")
    completed = sum(1 for b in broadcasts if b.status == "completed")
    cancelled = sum(1 for b in broadcasts if b.status == "cancelled")
    
    # Процент успешных отправок
    total_attempts = total_sent + total_failed
    success_rate = round((total_sent / total_attempts * 100) if total_attempts > 0 else 0, 2)
    
    return BroadcastStatsResponse(
        total_broadcasts=total_broadcasts,
        total_sent=total_sent,
        total_failed=total_failed,
        pending=pending,
        running=running,
        completed=completed,
        cancelled=cancelled,
        success_rate=success_rate
    )


def is_broadcast_cancelled(broadcast_id: int) -> bool:
    """
    Проверка, отменена ли рассылка.
    Используется в broadcast_worker для остановки.
    """
    if broadcast_id not in _active_broadcasts:
        return True
    return _active_broadcasts[broadcast_id].get("cancelled", False)


def remove_active_broadcast(broadcast_id: int) -> None:
    """
    Удаление рассылки из активных после завершения.
    """
    _active_broadcasts.pop(broadcast_id, None)
