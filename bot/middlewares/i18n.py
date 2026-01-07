"""
Middleware для определения языка пользователя.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.models import User
from bot.config import config
from bot.locales import get_text


class I18nMiddleware(BaseMiddleware):
    """Middleware для определения языка и функции перевода."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User | None = data.get('user')
        
        # Определяем язык
        if user is not None:
            lang = user.language or config.DEFAULT_LANGUAGE
        else:
            lang = config.DEFAULT_LANGUAGE
        
        # Передаём язык и функцию перевода
        data['lang'] = lang
        data['_'] = lambda key, **kwargs: get_text(key, lang, **kwargs)
        
        return await handler(event, data)
