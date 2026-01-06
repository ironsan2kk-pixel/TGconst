"""
API эндпоинты для управления каналами бота
"""
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Path
from sqlalchemy import select, func

from ..models.bot_db import Channel, Tariff
from ..schemas.channel import (
    ChannelCreate, ChannelUpdate, ChannelResponse, ChannelListResponse
)
from .deps import BotDbSession, CurrentAdmin

router = APIRouter()


@router.get(
    "",
    response_model=ChannelListResponse,
    summary="Список каналов",
    description="Получение списка всех каналов бота"
)
async def get_channels(
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> ChannelListResponse:
    """Получить список всех каналов бота"""
    # Получаем общее количество
    count_result = await bot_db.execute(select(func.count(Channel.id)))
    total = count_result.scalar() or 0
    
    # Получаем список каналов
    result = await bot_db.execute(
        select(Channel).order_by(Channel.created_at.desc())
    )
    channels = result.scalars().all()
    
    # Формируем ответ с количеством тарифов
    items = []
    for channel in channels:
        # Считаем количество тарифов для каждого канала
        tariffs_count_result = await bot_db.execute(
            select(func.count(Tariff.id)).where(Tariff.channel_id == channel.id)
        )
        tariffs_count = tariffs_count_result.scalar() or 0
        
        channel_data = ChannelResponse(
            id=channel.id,
            channel_id=channel.channel_id,
            channel_username=channel.channel_username,
            title=channel.title,
            is_active=channel.is_active,
            created_at=channel.created_at,
            tariffs_count=tariffs_count
        )
        items.append(channel_data)
    
    return ChannelListResponse(total=total, items=items)


@router.post(
    "",
    response_model=ChannelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить канал",
    description="Добавление нового канала для продажи доступа"
)
async def create_channel(
    data: ChannelCreate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> ChannelResponse:
    """
    Добавить новый канал.
    
    Канал должен иметь уникальный channel_id (Telegram ID).
    """
    # Проверяем что канал не добавлен
    existing = await bot_db.execute(
        select(Channel).where(Channel.channel_id == data.channel_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Канал с таким ID уже добавлен"
        )
    
    # Создаём канал
    channel = Channel(
        channel_id=data.channel_id,
        channel_username=data.channel_username,
        title=data.title,
        is_active=data.is_active
    )
    
    bot_db.add(channel)
    await bot_db.commit()
    await bot_db.refresh(channel)
    
    return ChannelResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        channel_username=channel.channel_username,
        title=channel.title,
        is_active=channel.is_active,
        created_at=channel.created_at,
        tariffs_count=0
    )


@router.get(
    "/{channel_id}",
    response_model=ChannelResponse,
    summary="Получить канал",
    description="Получение информации о конкретном канале"
)
async def get_channel(
    channel_id: Annotated[int, Path(description="ID канала в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> ChannelResponse:
    """Получить канал по ID"""
    result = await bot_db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Канал не найден"
        )
    
    # Считаем количество тарифов
    tariffs_count_result = await bot_db.execute(
        select(func.count(Tariff.id)).where(Tariff.channel_id == channel.id)
    )
    tariffs_count = tariffs_count_result.scalar() or 0
    
    return ChannelResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        channel_username=channel.channel_username,
        title=channel.title,
        is_active=channel.is_active,
        created_at=channel.created_at,
        tariffs_count=tariffs_count
    )


@router.put(
    "/{channel_id}",
    response_model=ChannelResponse,
    summary="Обновить канал",
    description="Обновление настроек канала"
)
async def update_channel(
    channel_id: Annotated[int, Path(description="ID канала в БД")],
    data: ChannelUpdate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> ChannelResponse:
    """Обновить настройки канала"""
    result = await bot_db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Канал не найден"
        )
    
    # Если меняем channel_id — проверяем уникальность
    if data.channel_id and data.channel_id != channel.channel_id:
        existing = await bot_db.execute(
            select(Channel).where(
                Channel.channel_id == data.channel_id,
                Channel.id != channel.id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Канал с таким Telegram ID уже добавлен"
            )
    
    # Обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)
    
    await bot_db.commit()
    await bot_db.refresh(channel)
    
    # Считаем количество тарифов
    tariffs_count_result = await bot_db.execute(
        select(func.count(Tariff.id)).where(Tariff.channel_id == channel.id)
    )
    tariffs_count = tariffs_count_result.scalar() or 0
    
    return ChannelResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        channel_username=channel.channel_username,
        title=channel.title,
        is_active=channel.is_active,
        created_at=channel.created_at,
        tariffs_count=tariffs_count
    )


@router.delete(
    "/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить канал",
    description="Удаление канала и всех его тарифов"
)
async def delete_channel(
    channel_id: Annotated[int, Path(description="ID канала в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> None:
    """
    Удалить канал.
    
    При удалении:
    - Удаляются все тарифы канала (каскадно)
    - Подписки на канал становятся неактивными
    """
    result = await bot_db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Канал не найден"
        )
    
    # Удаляем канал (тарифы удалятся каскадно)
    await bot_db.delete(channel)
    await bot_db.commit()
