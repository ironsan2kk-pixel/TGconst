"""
Middleware для проверки бана пользователя.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from bot.models import User
from bot.locales import get_text


class BanMiddleware(BaseMiddleware):
    """Middleware для проверки заблокированных пользователей."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User | None = data.get('user')
        
        if user is not None and user.is_banned:
            lang = user.language or 'ru'
            reason = user.ban_reason or 'Не указана'
            text = get_text('banned', lang, reason=reason)
            
            if isinstance(event, Message):
                await event.answer(text)
                return None
            elif isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
                return None
        
        return await handler(event, data)
