"""
API эндпоинты для управления ботами
"""
import uuid as uuid_lib
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Path
from sqlalchemy import select, func

from ..models.main_db import Bot
from ..schemas.bot import (
    BotCreate, BotUpdate, BotResponse, 
    BotListResponse, BotStatusResponse
)
from ..database import init_bot_db, delete_bot_db
from ..services.bot_manager import get_bot_manager
from .deps import DbSession, CurrentAdmin

router = APIRouter()


@router.get(
    "",
    response_model=BotListResponse,
    summary="Список ботов",
    description="Получение списка всех созданных ботов"
)
async def get_bots(
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotListResponse:
    """Получить список всех ботов"""
    # Получаем общее количество
    count_result = await db.execute(select(func.count(Bot.id)))
    total = count_result.scalar()
    
    # Получаем список ботов
    result = await db.execute(
        select(Bot).order_by(Bot.created_at.desc())
    )
    bots = result.scalars().all()
    
    return BotListResponse(
        total=total,
        items=[BotResponse.model_validate(bot) for bot in bots]
    )


@router.post(
    "",
    response_model=BotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать бота",
    description="Создание нового бота с автоматическим созданием базы данных"
)
async def create_bot(
    data: BotCreate,
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotResponse:
    """
    Создать нового бота.
    
    При создании:
    - Генерируется UUID для бота
    - Создаётся папка data/bots/{uuid}/
    - Создаётся база данных bot.db с таблицами
    """
    # Проверяем что токен не используется
    existing = await db.execute(
        select(Bot).where(Bot.bot_token == data.bot_token)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Бот с таким токеном уже существует"
        )
    
    # Генерируем UUID
    bot_uuid = str(uuid_lib.uuid4())
    
    # Создаём запись в БД
    bot = Bot(
        uuid=bot_uuid,
        name=data.name,
        bot_token=data.bot_token,
        cryptobot_token=data.cryptobot_token,
        welcome_message=data.welcome_message,
        support_url=data.support_url,
        is_active=False
    )
    
    db.add(bot)
    await db.flush()
    
    # Создаём папку и БД для бота
    try:
        await init_bot_db(bot_uuid)
    except Exception as e:
        # Если не удалось создать БД — откатываем транзакцию
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания базы данных бота: {str(e)}"
        )
    
    await db.commit()
    await db.refresh(bot)
    
    return BotResponse.model_validate(bot)


@router.get(
    "/{bot_uuid}",
    response_model=BotResponse,
    summary="Получить бота",
    description="Получение информации о конкретном боте по UUID"
)
async def get_bot(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotResponse:
    """Получить бота по UUID"""
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    return BotResponse.model_validate(bot)


@router.put(
    "/{bot_uuid}",
    response_model=BotResponse,
    summary="Обновить бота",
    description="Обновление настроек бота"
)
async def update_bot(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    data: BotUpdate,
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotResponse:
    """Обновить настройки бота"""
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    # Если меняем токен — проверяем уникальность
    if data.bot_token and data.bot_token != bot.bot_token:
        existing = await db.execute(
            select(Bot).where(
                Bot.bot_token == data.bot_token,
                Bot.id != bot.id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Бот с таким токеном уже существует"
            )
    
    # Обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)
    
    await db.commit()
    await db.refresh(bot)
    
    return BotResponse.model_validate(bot)


@router.delete(
    "/{bot_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить бота",
    description="Удаление бота и всех его данных"
)
async def delete_bot(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    db: DbSession,
    current_admin: CurrentAdmin
) -> None:
    """
    Удалить бота.
    
    При удалении:
    - Останавливается процесс бота (если запущен)
    - Удаляется папка data/bots/{uuid}/ с БД
    - Удаляется запись из main.db
    """
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    # Останавливаем процесс если запущен
    bot_manager = get_bot_manager()
    if bot_manager.is_running(bot_uuid):
        await bot_manager.stop_bot(bot_uuid, db)
    
    # Удаляем папку и БД бота
    try:
        await delete_bot_db(bot_uuid)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка удаления данных бота: {str(e)}"
        )
    
    # Удаляем запись из main.db
    await db.delete(bot)
    await db.commit()


@router.post(
    "/{bot_uuid}/start",
    response_model=BotStatusResponse,
    summary="Запустить бота",
    description="Запуск процесса бота"
)
async def start_bot(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotStatusResponse:
    """
    Запустить бота.
    
    Запускает процесс бота как subprocess и сохраняет PID в БД.
    """
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    # Используем BotManager для запуска
    bot_manager = get_bot_manager()
    start_result = await bot_manager.start_bot(bot_uuid, db)
    
    if not start_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=start_result["message"]
        )
    
    # Обновляем данные из БД
    await db.refresh(bot)
    
    return BotStatusResponse(
        uuid=bot_uuid,
        is_active=True,
        process_pid=start_result.get("pid"),
        message=start_result["message"]
    )


@router.post(
    "/{bot_uuid}/stop",
    response_model=BotStatusResponse,
    summary="Остановить бота",
    description="Остановка процесса бота"
)
async def stop_bot(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotStatusResponse:
    """
    Остановить бота.
    
    Останавливает процесс бота по PID и обновляет статус в БД.
    """
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    # Используем BotManager для остановки
    bot_manager = get_bot_manager()
    stop_result = await bot_manager.stop_bot(bot_uuid, db)
    
    if not stop_result["success"] and not stop_result.get("already_stopped"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=stop_result["message"]
        )
    
    # Обновляем данные из БД
    await db.refresh(bot)
    
    return BotStatusResponse(
        uuid=bot_uuid,
        is_active=False,
        process_pid=None,
        message=stop_result["message"]
    )


@router.get(
    "/{bot_uuid}/status",
    response_model=BotStatusResponse,
    summary="Статус бота",
    description="Получение текущего статуса бота"
)
async def get_bot_status(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotStatusResponse:
    """Получить текущий статус бота"""
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    # Получаем актуальный статус из BotManager
    bot_manager = get_bot_manager()
    manager_status = await bot_manager.get_status(bot_uuid)
    
    is_running = manager_status["is_running"]
    pid = manager_status["pid"]
    uptime = manager_status.get("uptime_seconds")
    
    if is_running:
        status_msg = f"Бот запущен (PID: {pid}, uptime: {uptime}s)"
    else:
        status_msg = "Бот остановлен"
    
    return BotStatusResponse(
        uuid=bot_uuid,
        is_active=is_running,
        process_pid=pid,
        message=status_msg
    )


@router.post(
    "/{bot_uuid}/restart",
    response_model=BotStatusResponse,
    summary="Перезапустить бота",
    description="Перезапуск процесса бота"
)
async def restart_bot(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    db: DbSession,
    current_admin: CurrentAdmin
) -> BotStatusResponse:
    """
    Перезапустить бота.
    
    Останавливает и затем запускает процесс бота.
    """
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    # Используем BotManager для перезапуска
    bot_manager = get_bot_manager()
    restart_result = await bot_manager.restart_bot(bot_uuid, db)
    
    if not restart_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=restart_result["message"]
        )
    
    return BotStatusResponse(
        uuid=bot_uuid,
        is_active=True,
        process_pid=restart_result.get("pid"),
        message=restart_result["message"]
    )


@router.get(
    "/manager/status",
    summary="Статус менеджера ботов",
    description="Получить статус всех запущенных ботов"
)
async def get_bot_manager_status(
    current_admin: CurrentAdmin
) -> dict:
    """Получить статус всех ботов от BotManager"""
    bot_manager = get_bot_manager()
    all_status = bot_manager.get_all_status()
    
    return {
        "running_count": len(all_status),
        "bots": all_status
    }


@router.post(
    "/subscriptions/check",
    summary="Проверить подписки",
    description="Немедленная проверка всех подписок во всех ботах"
)
async def check_subscriptions(
    current_admin: CurrentAdmin
) -> dict:
    """
    Выполнить немедленную проверку подписок.
    
    Проверяет все активные боты:
    - Кикает пользователей с истёкшими подписками
    - Отправляет уведомления тем, у кого подписка истекает через 1 день
    """
    from ..services.subscription_checker import get_subscription_checker
    
    checker = get_subscription_checker()
    result = await checker.check_now()
    
    return {
        "success": True,
        "message": "Проверка завершена",
        "result": result
    }


@router.get(
    "/subscriptions/checker-status",
    summary="Статус проверки подписок",
    description="Получить статус фоновой задачи проверки подписок"
)
async def get_subscription_checker_status(
    current_admin: CurrentAdmin
) -> dict:
    """Получить статус subscription checker"""
    from ..services.subscription_checker import get_subscription_checker
    
    checker = get_subscription_checker()
    
    return {
        "is_running": checker.is_running,
        "check_interval_seconds": 300,
        "notify_before_days": 1
    }
