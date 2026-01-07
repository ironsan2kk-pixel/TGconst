"""
Middleware для регистрации и обновления пользователей.
"""

from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, User as TgUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.config import config
from bot.services.notifications import notify_new_user


class UserMiddleware(BaseMiddleware):
    """Middleware для автоматической регистрации пользователей."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Получаем Telegram user
        tg_user: TgUser | None = None
        
        if isinstance(event, Message):
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery):
            tg_user = event.from_user
        
        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)
        
        session: AsyncSession = data.get('session')
        if session is None:
            return await handler(event, data)
        
        # Ищем или создаём пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == tg_user.id)
        )
        user = result.scalar_one_or_none()
        
        is_new_user = False
        
        if user is None:
            # Создаём нового пользователя
            user = User(
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                language=config.DEFAULT_LANGUAGE,
            )
            session.add(user)
            await session.flush()
            is_new_user = True
        else:
            # Обновляем данные
            user.username = tg_user.username
            user.first_name = tg_user.first_name
            user.last_name = tg_user.last_name
            user.last_activity = datetime.utcnow()
        
        # Передаём пользователя в data
        data['user'] = user
        data['is_new_user'] = is_new_user
        
        # Выполняем хендлер
        result = await handler(event, data)
        
        # Уведомляем админов о новом пользователе
        if is_new_user and config.NOTIFY_NEW_USERS:
            from bot.loader import bot
            await notify_new_user(bot, user)
        
        return result
