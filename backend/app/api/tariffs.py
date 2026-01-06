"""
API эндпоинты для управления тарифами
"""
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Path
from sqlalchemy import select, func

from ..models.bot_db import Channel, Tariff
from ..schemas.tariff import (
    TariffCreate, TariffUpdate, TariffResponse, TariffListResponse
)
from .deps import BotDbSession, CurrentAdmin

router = APIRouter()


async def get_channel_or_404(bot_db, channel_id: int) -> Channel:
    """Вспомогательная функция для получения канала или 404"""
    result = await bot_db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Канал не найден"
        )
    
    return channel


async def get_tariff_or_404(bot_db, tariff_id: int) -> Tariff:
    """Вспомогательная функция для получения тарифа или 404"""
    result = await bot_db.execute(
        select(Tariff).where(Tariff.id == tariff_id)
    )
    tariff = result.scalar_one_or_none()
    
    if tariff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тариф не найден"
        )
    
    return tariff


@router.get(
    "/channels/{channel_id}/tariffs",
    response_model=TariffListResponse,
    summary="Список тарифов канала",
    description="Получение списка всех тарифов конкретного канала"
)
async def get_channel_tariffs(
    channel_id: Annotated[int, Path(description="ID канала в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> TariffListResponse:
    """Получить список тарифов канала"""
    # Проверяем существование канала
    await get_channel_or_404(bot_db, channel_id)
    
    # Получаем общее количество
    count_result = await bot_db.execute(
        select(func.count(Tariff.id)).where(Tariff.channel_id == channel_id)
    )
    total = count_result.scalar() or 0
    
    # Получаем список тарифов
    result = await bot_db.execute(
        select(Tariff)
        .where(Tariff.channel_id == channel_id)
        .order_by(Tariff.sort_order, Tariff.created_at)
    )
    tariffs = result.scalars().all()
    
    return TariffListResponse(
        total=total,
        channel_id=channel_id,
        items=[TariffResponse.model_validate(t) for t in tariffs]
    )


@router.post(
    "/channels/{channel_id}/tariffs",
    response_model=TariffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тариф",
    description="Создание нового тарифа для канала"
)
async def create_tariff(
    channel_id: Annotated[int, Path(description="ID канала в БД")],
    data: TariffCreate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> TariffResponse:
    """
    Создать новый тариф для канала.
    
    Тариф определяет цену и срок подписки на канал.
    """
    # Проверяем существование канала
    await get_channel_or_404(bot_db, channel_id)
    
    # Если sort_order не указан, ставим в конец
    if data.sort_order == 0:
        max_order_result = await bot_db.execute(
            select(func.max(Tariff.sort_order)).where(Tariff.channel_id == channel_id)
        )
        max_order = max_order_result.scalar() or 0
        data.sort_order = max_order + 1
    
    # Создаём тариф
    tariff = Tariff(
        channel_id=channel_id,
        name=data.name,
        price=data.price,
        duration_days=data.duration_days,
        is_active=data.is_active,
        sort_order=data.sort_order
    )
    
    bot_db.add(tariff)
    await bot_db.commit()
    await bot_db.refresh(tariff)
    
    return TariffResponse.model_validate(tariff)


@router.get(
    "/tariffs/{tariff_id}",
    response_model=TariffResponse,
    summary="Получить тариф",
    description="Получение информации о конкретном тарифе"
)
async def get_tariff(
    tariff_id: Annotated[int, Path(description="ID тарифа в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> TariffResponse:
    """Получить тариф по ID"""
    tariff = await get_tariff_or_404(bot_db, tariff_id)
    return TariffResponse.model_validate(tariff)


@router.put(
    "/tariffs/{tariff_id}",
    response_model=TariffResponse,
    summary="Обновить тариф",
    description="Обновление настроек тарифа"
)
async def update_tariff(
    tariff_id: Annotated[int, Path(description="ID тарифа в БД")],
    data: TariffUpdate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> TariffResponse:
    """Обновить настройки тарифа"""
    tariff = await get_tariff_or_404(bot_db, tariff_id)
    
    # Обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tariff, field, value)
    
    await bot_db.commit()
    await bot_db.refresh(tariff)
    
    return TariffResponse.model_validate(tariff)


@router.delete(
    "/tariffs/{tariff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тариф",
    description="Удаление тарифа"
)
async def delete_tariff(
    tariff_id: Annotated[int, Path(description="ID тарифа в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> None:
    """
    Удалить тариф.
    
    Примечание: Существующие подписки с этим тарифом останутся активными,
    но поле tariff_id станет NULL.
    """
    tariff = await get_tariff_or_404(bot_db, tariff_id)
    
    await bot_db.delete(tariff)
    await bot_db.commit()


@router.post(
    "/tariffs/{tariff_id}/toggle",
    response_model=TariffResponse,
    summary="Переключить статус тарифа",
    description="Быстрое включение/выключение тарифа"
)
async def toggle_tariff(
    tariff_id: Annotated[int, Path(description="ID тарифа в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> TariffResponse:
    """Переключить статус активности тарифа"""
    tariff = await get_tariff_or_404(bot_db, tariff_id)
    
    tariff.is_active = not tariff.is_active
    
    await bot_db.commit()
    await bot_db.refresh(tariff)
    
    return TariffResponse.model_validate(tariff)


@router.post(
    "/channels/{channel_id}/tariffs/reorder",
    response_model=TariffListResponse,
    summary="Изменить порядок тарифов",
    description="Изменение порядка отображения тарифов"
)
async def reorder_tariffs(
    channel_id: Annotated[int, Path(description="ID канала в БД")],
    tariff_ids: list[int],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> TariffListResponse:
    """
    Изменить порядок тарифов.
    
    Принимает список ID тарифов в желаемом порядке.
    """
    # Проверяем существование канала
    await get_channel_or_404(bot_db, channel_id)
    
    # Обновляем sort_order для каждого тарифа
    for index, tariff_id in enumerate(tariff_ids):
        result = await bot_db.execute(
            select(Tariff).where(
                Tariff.id == tariff_id,
                Tariff.channel_id == channel_id
            )
        )
        tariff = result.scalar_one_or_none()
        
        if tariff:
            tariff.sort_order = index + 1
    
    await bot_db.commit()
    
    # Возвращаем обновлённый список
    count_result = await bot_db.execute(
        select(func.count(Tariff.id)).where(Tariff.channel_id == channel_id)
    )
    total = count_result.scalar() or 0
    
    result = await bot_db.execute(
        select(Tariff)
        .where(Tariff.channel_id == channel_id)
        .order_by(Tariff.sort_order, Tariff.created_at)
    )
    tariffs = result.scalars().all()
    
    return TariffListResponse(
        total=total,
        channel_id=channel_id,
        items=[TariffResponse.model_validate(t) for t in tariffs]
    )
