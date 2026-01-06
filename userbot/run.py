#!/usr/bin/env python3
"""
Точка входа Userbot

Запускает:
1. Pyrogram клиент для добавления/удаления пользователей
2. HTTP API для получения задач от backend

Запуск:
    python userbot/run.py
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from config import get_settings
from client import get_userbot_client, UserbotClient
from actions.invite import process_invite_task, kick_user_from_channel_task

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
settings = get_settings()


# === Pydantic модели ===

class InviteRequest(BaseModel):
    """Запрос на добавление пользователя в канал"""
    bot_uuid: str
    user_telegram_id: int
    channel_id: int  # ID канала в БД бота (не telegram_id)
    subscription_id: int


class KickRequest(BaseModel):
    """Запрос на удаление пользователя из канала"""
    bot_uuid: str
    user_telegram_id: int
    channel_id: int
    subscription_id: int


class TaskResult(BaseModel):
    """Результат выполнения задачи"""
    success: bool
    error: Optional[str] = None
    task_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str
    userbot_connected: bool
    userbot_info: Optional[dict] = None


# === Глобальные переменные ===

userbot_client: Optional[UserbotClient] = None


# === Lifespan ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    global userbot_client
    
    logger.info("=" * 50)
    logger.info("Запуск Userbot сервера...")
    logger.info("=" * 50)
    
    # Подключаем userbot
    userbot_client = get_userbot_client()
    
    if settings.is_configured:
        connected = await userbot_client.connect()
        if connected:
            logger.info("✅ Userbot подключен к Telegram")
        else:
            logger.warning("⚠️ Userbot не удалось подключить")
    else:
        logger.warning(
            "⚠️ Userbot не настроен. "
            "Установите USERBOT_API_ID, USERBOT_API_HASH и USERBOT_SESSION_STRING в .env"
        )
    
    yield
    
    # Отключаем userbot
    logger.info("Остановка Userbot...")
    if userbot_client and userbot_client.is_connected:
        await userbot_client.disconnect()
    
    logger.info("Userbot остановлен")


# === FastAPI приложение ===

app = FastAPI(
    title="Userbot API",
    description="API для управления добавлением/удалением пользователей в каналы",
    version="1.0.0",
    lifespan=lifespan
)


# === Эндпоинты ===

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния сервиса"""
    global userbot_client
    
    is_connected = userbot_client.is_connected if userbot_client else False
    userbot_info = None
    
    if is_connected:
        userbot_info = await userbot_client.get_me()
    
    return HealthResponse(
        status="ok",
        userbot_connected=is_connected,
        userbot_info=userbot_info
    )


@app.post("/invite", response_model=TaskResult)
async def invite_user(request: InviteRequest, background_tasks: BackgroundTasks):
    """
    Добавить пользователя в канал
    
    Выполняется асинхронно в фоне.
    """
    global userbot_client
    
    if not userbot_client or not userbot_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Userbot не подключен к Telegram"
        )
    
    # Генерируем ID задачи
    import uuid
    task_id = str(uuid.uuid4())[:8]
    
    logger.info(
        f"[{task_id}] Получена задача invite: "
        f"user={request.user_telegram_id}, channel={request.channel_id}"
    )
    
    # Выполняем в фоне
    background_tasks.add_task(
        process_invite_task,
        bot_uuid=request.bot_uuid,
        user_telegram_id=request.user_telegram_id,
        channel_id=request.channel_id,
        subscription_id=request.subscription_id
    )
    
    return TaskResult(
        success=True,
        error=None,
        task_id=task_id
    )


@app.post("/invite/sync", response_model=TaskResult)
async def invite_user_sync(request: InviteRequest):
    """
    Добавить пользователя в канал (синхронно)
    
    Ждёт результата выполнения.
    """
    global userbot_client
    
    if not userbot_client or not userbot_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Userbot не подключен к Telegram"
        )
    
    result = await process_invite_task(
        bot_uuid=request.bot_uuid,
        user_telegram_id=request.user_telegram_id,
        channel_id=request.channel_id,
        subscription_id=request.subscription_id
    )
    
    return TaskResult(
        success=result["success"],
        error=result.get("error")
    )


@app.post("/kick", response_model=TaskResult)
async def kick_user(request: KickRequest, background_tasks: BackgroundTasks):
    """
    Удалить пользователя из канала
    
    Выполняется асинхронно в фоне.
    """
    global userbot_client
    
    if not userbot_client or not userbot_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Userbot не подключен к Telegram"
        )
    
    import uuid
    task_id = str(uuid.uuid4())[:8]
    
    logger.info(
        f"[{task_id}] Получена задача kick: "
        f"user={request.user_telegram_id}, channel={request.channel_id}"
    )
    
    background_tasks.add_task(
        kick_user_from_channel_task,
        bot_uuid=request.bot_uuid,
        user_telegram_id=request.user_telegram_id,
        channel_id=request.channel_id,
        subscription_id=request.subscription_id
    )
    
    return TaskResult(
        success=True,
        error=None,
        task_id=task_id
    )


@app.post("/kick/sync", response_model=TaskResult)
async def kick_user_sync(request: KickRequest):
    """
    Удалить пользователя из канала (синхронно)
    """
    global userbot_client
    
    if not userbot_client or not userbot_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Userbot не подключен к Telegram"
        )
    
    result = await kick_user_from_channel_task(
        bot_uuid=request.bot_uuid,
        user_telegram_id=request.user_telegram_id,
        channel_id=request.channel_id,
        subscription_id=request.subscription_id
    )
    
    return TaskResult(
        success=result["success"],
        error=result.get("error")
    )


@app.post("/reconnect")
async def reconnect_userbot():
    """Переподключить userbot"""
    global userbot_client
    
    if userbot_client:
        await userbot_client.disconnect()
        connected = await userbot_client.connect()
        
        return {
            "success": connected,
            "message": "Переподключение успешно" if connected else "Не удалось переподключиться"
        }
    
    return {"success": False, "message": "Клиент не инициализирован"}


@app.get("/channel/{channel_id}")
async def get_channel_info(channel_id: int):
    """Получить информацию о канале"""
    global userbot_client
    
    if not userbot_client or not userbot_client.is_connected:
        raise HTTPException(status_code=503, detail="Userbot не подключен")
    
    info = await userbot_client.get_channel_info(channel_id)
    
    if info is None:
        raise HTTPException(status_code=404, detail="Канал не найден")
    
    return info


@app.get("/check/{channel_id}/{user_id}")
async def check_user_in_channel(channel_id: int, user_id: int):
    """Проверить, находится ли пользователь в канале"""
    global userbot_client
    
    if not userbot_client or not userbot_client.is_connected:
        raise HTTPException(status_code=503, detail="Userbot не подключен")
    
    is_member = await userbot_client.check_user_in_channel(user_id, channel_id)
    
    return {
        "user_id": user_id,
        "channel_id": channel_id,
        "is_member": is_member
    }


# === Запуск ===

def main():
    """Главная функция"""
    logger.info(f"Userbot API запускается на {settings.USERBOT_HOST}:{settings.USERBOT_PORT}")
    
    uvicorn.run(
        "run:app",
        host=settings.USERBOT_HOST,
        port=settings.USERBOT_PORT,
        reload=settings.is_configured is False,  # reload только если не настроен
        log_level="info"
    )


if __name__ == "__main__":
    main()
