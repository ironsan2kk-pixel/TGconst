"""
API эндпоинты для управления промокодами
"""
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, status, Path, Query
from sqlalchemy import select, func

from ..models.bot_db import Promocode
from ..schemas.promocode import (
    PromocodeCreate, 
    PromocodeUpdate, 
    PromocodeResponse, 
    PromocodeListResponse,
    PromocodeValidateRequest,
    PromocodeValidateResponse,
    PromocodeClearLimitRequest
)
from .deps import BotDbSession, CurrentAdmin

router = APIRouter()


def promocode_to_response(promocode: Promocode) -> PromocodeResponse:
    """Преобразование модели в ответ с вычислением is_valid"""
    return PromocodeResponse(
        id=promocode.id,
        code=promocode.code,
        discount_percent=promocode.discount_percent,
        discount_amount=promocode.discount_amount,
        max_uses=promocode.max_uses,
        used_count=promocode.used_count,
        valid_from=promocode.valid_from,
        valid_until=promocode.valid_until,
        is_active=promocode.is_active,
        is_valid=promocode.is_valid(),
        created_at=promocode.created_at
    )


async def get_promocode_or_404(bot_db, promocode_id: int) -> Promocode:
    """Вспомогательная функция для получения промокода или 404"""
    result = await bot_db.execute(
        select(Promocode).where(Promocode.id == promocode_id)
    )
    promocode = result.scalar_one_or_none()
    
    if promocode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Промокод не найден"
        )
    
    return promocode


@router.get(
    "",
    response_model=PromocodeListResponse,
    summary="Список промокодов",
    description="Получение списка всех промокодов бота"
)
async def get_promocodes(
    bot_db: BotDbSession,
    current_admin: CurrentAdmin,
    is_active: Annotated[Optional[bool], Query(description="Фильтр по активности")] = None,
    is_valid: Annotated[Optional[bool], Query(description="Фильтр по валидности")] = None
) -> PromocodeListResponse:
    """
    Получить список всех промокодов.
    
    Можно фильтровать по:
    - is_active: только активные или только неактивные
    - is_valid: только валидные (можно использовать) или невалидные
    """
    # Базовый запрос
    query = select(Promocode)
    
    # Фильтр по активности
    if is_active is not None:
        query = query.where(Promocode.is_active == is_active)
    
    # Выполняем запрос
    result = await bot_db.execute(query.order_by(Promocode.created_at.desc()))
    promocodes = result.scalars().all()
    
    # Преобразуем в ответы и фильтруем по is_valid если нужно
    items = []
    for promo in promocodes:
        promo_response = promocode_to_response(promo)
        if is_valid is None or promo_response.is_valid == is_valid:
            items.append(promo_response)
    
    # Считаем статистику
    total = len(items)
    active_count = sum(1 for p in items if p.is_active and p.is_valid)
    
    return PromocodeListResponse(
        total=total,
        active_count=active_count,
        items=items
    )


@router.post(
    "",
    response_model=PromocodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать промокод",
    description="Создание нового промокода со скидкой"
)
async def create_promocode(
    data: PromocodeCreate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> PromocodeResponse:
    """
    Создать новый промокод.
    
    Можно указать либо discount_percent (скидка в %), либо discount_amount (фикс. скидка в USD).
    """
    # Проверяем уникальность кода
    result = await bot_db.execute(
        select(Promocode).where(Promocode.code == data.code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Промокод с кодом '{data.code}' уже существует"
        )
    
    # Создаём промокод
    promocode = Promocode(
        code=data.code,
        discount_percent=data.discount_percent,
        discount_amount=data.discount_amount,
        max_uses=data.max_uses,
        used_count=0,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        is_active=data.is_active
    )
    
    bot_db.add(promocode)
    await bot_db.commit()
    await bot_db.refresh(promocode)
    
    return promocode_to_response(promocode)


@router.get(
    "/{promocode_id}",
    response_model=PromocodeResponse,
    summary="Получить промокод",
    description="Получение информации о конкретном промокоде"
)
async def get_promocode(
    promocode_id: Annotated[int, Path(description="ID промокода в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> PromocodeResponse:
    """Получить промокод по ID"""
    promocode = await get_promocode_or_404(bot_db, promocode_id)
    return promocode_to_response(promocode)


@router.put(
    "/{promocode_id}",
    response_model=PromocodeResponse,
    summary="Обновить промокод",
    description="Обновление настроек промокода"
)
async def update_promocode(
    promocode_id: Annotated[int, Path(description="ID промокода в БД")],
    data: PromocodeUpdate,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> PromocodeResponse:
    """Обновить настройки промокода"""
    promocode = await get_promocode_or_404(bot_db, promocode_id)
    
    # Если меняем код — проверяем уникальность
    if data.code and data.code != promocode.code:
        result = await bot_db.execute(
            select(Promocode).where(Promocode.code == data.code)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Промокод с кодом '{data.code}' уже существует"
            )
    
    # Обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(promocode, field, value)
    
    await bot_db.commit()
    await bot_db.refresh(promocode)
    
    return promocode_to_response(promocode)


@router.delete(
    "/{promocode_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить промокод",
    description="Удаление промокода"
)
async def delete_promocode(
    promocode_id: Annotated[int, Path(description="ID промокода в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> None:
    """
    Удалить промокод.
    
    Примечание: Информация о скидках в уже созданных платежах сохранится.
    """
    promocode = await get_promocode_or_404(bot_db, promocode_id)
    
    await bot_db.delete(promocode)
    await bot_db.commit()


@router.post(
    "/{promocode_id}/toggle",
    response_model=PromocodeResponse,
    summary="Переключить статус",
    description="Быстрое включение/выключение промокода"
)
async def toggle_promocode(
    promocode_id: Annotated[int, Path(description="ID промокода в БД")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> PromocodeResponse:
    """Переключить статус активности промокода"""
    promocode = await get_promocode_or_404(bot_db, promocode_id)
    
    promocode.is_active = not promocode.is_active
    
    await bot_db.commit()
    await bot_db.refresh(promocode)
    
    return promocode_to_response(promocode)


@router.post(
    "/{promocode_id}/reset",
    response_model=PromocodeResponse,
    summary="Сбросить счётчик",
    description="Сброс счётчика использований и/или лимита"
)
async def reset_promocode_usage(
    promocode_id: Annotated[int, Path(description="ID промокода в БД")],
    data: PromocodeClearLimitRequest,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> PromocodeResponse:
    """
    Сбросить счётчик использований промокода.
    
    Можно также установить новый лимит использований.
    """
    promocode = await get_promocode_or_404(bot_db, promocode_id)
    
    if data.reset_count:
        promocode.used_count = 0
    
    if data.new_max_uses is not None:
        promocode.max_uses = data.new_max_uses
    
    await bot_db.commit()
    await bot_db.refresh(promocode)
    
    return promocode_to_response(promocode)


@router.post(
    "/validate",
    response_model=PromocodeValidateResponse,
    summary="Проверить промокод",
    description="Проверка валидности промокода и расчёт скидки"
)
async def validate_promocode(
    data: PromocodeValidateRequest,
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> PromocodeValidateResponse:
    """
    Проверить промокод и рассчитать скидку.
    
    Если указана цена — возвращает рассчитанную скидку и итоговую цену.
    
    Возможные причины невалидности (error):
    - "Промокод не найден"
    - "Промокод деактивирован"
    - "Промокод ещё не действует"
    - "Промокод истёк"
    - "Промокод использован максимальное число раз"
    """
    # Ищем промокод
    result = await bot_db.execute(
        select(Promocode).where(Promocode.code == data.code)
    )
    promocode = result.scalar_one_or_none()
    
    # Не найден
    if promocode is None:
        return PromocodeValidateResponse(
            valid=False,
            code=data.code,
            error="Промокод не найден"
        )
    
    # Проверяем валидность с детальной причиной
    now = datetime.utcnow()
    
    if not promocode.is_active:
        return PromocodeValidateResponse(
            valid=False,
            code=data.code,
            discount_percent=promocode.discount_percent,
            discount_amount=promocode.discount_amount,
            error="Промокод деактивирован"
        )
    
    if promocode.valid_from and now < promocode.valid_from:
        return PromocodeValidateResponse(
            valid=False,
            code=data.code,
            discount_percent=promocode.discount_percent,
            discount_amount=promocode.discount_amount,
            error="Промокод ещё не действует"
        )
    
    if promocode.valid_until and now > promocode.valid_until:
        return PromocodeValidateResponse(
            valid=False,
            code=data.code,
            discount_percent=promocode.discount_percent,
            discount_amount=promocode.discount_amount,
            error="Промокод истёк"
        )
    
    if promocode.max_uses is not None and promocode.used_count >= promocode.max_uses:
        return PromocodeValidateResponse(
            valid=False,
            code=data.code,
            discount_percent=promocode.discount_percent,
            discount_amount=promocode.discount_amount,
            error="Промокод использован максимальное число раз"
        )
    
    # Промокод валиден — рассчитываем скидку если указана цена
    calculated_discount = None
    final_price = None
    
    if data.price is not None:
        calculated_discount = promocode.calculate_discount(data.price)
        calculated_discount = round(calculated_discount, 2)
        final_price = round(max(0, data.price - calculated_discount), 2)
    
    return PromocodeValidateResponse(
        valid=True,
        code=promocode.code,
        discount_percent=promocode.discount_percent,
        discount_amount=promocode.discount_amount,
        calculated_discount=calculated_discount,
        final_price=final_price,
        error=None
    )


@router.post(
    "/check/{code}",
    response_model=PromocodeValidateResponse,
    summary="Быстрая проверка по коду",
    description="Быстрая проверка промокода по коду (без тела запроса)"
)
async def check_promocode_by_code(
    code: Annotated[str, Path(description="Код промокода")],
    bot_db: BotDbSession,
    current_admin: CurrentAdmin,
    price: Annotated[Optional[float], Query(description="Цена для расчёта скидки")] = None
) -> PromocodeValidateResponse:
    """
    Быстрая проверка промокода по коду в URL.
    
    Удобно для быстрых проверок без отправки JSON-тела.
    """
    # Используем тот же метод
    data = PromocodeValidateRequest(code=code.upper(), price=price)
    return await validate_promocode(data, bot_db, current_admin)


@router.get(
    "/stats/summary",
    summary="Статистика промокодов",
    description="Общая статистика по промокодам"
)
async def get_promocodes_stats(
    bot_db: BotDbSession,
    current_admin: CurrentAdmin
) -> dict:
    """
    Получить общую статистику по промокодам.
    
    Возвращает:
    - total: всего промокодов
    - active: активных промокодов
    - valid: валидных (можно использовать сейчас)
    - total_uses: общее количество использований
    - expired: истёкших промокодов
    """
    # Получаем все промокоды
    result = await bot_db.execute(select(Promocode))
    promocodes = result.scalars().all()
    
    now = datetime.utcnow()
    
    total = len(promocodes)
    active = sum(1 for p in promocodes if p.is_active)
    valid = sum(1 for p in promocodes if p.is_valid())
    total_uses = sum(p.used_count for p in promocodes)
    expired = sum(1 for p in promocodes if p.valid_until and now > p.valid_until)
    exhausted = sum(1 for p in promocodes if p.max_uses and p.used_count >= p.max_uses)
    
    return {
        "total": total,
        "active": active,
        "valid": valid,
        "total_uses": total_uses,
        "expired": expired,
        "exhausted": exhausted
    }
