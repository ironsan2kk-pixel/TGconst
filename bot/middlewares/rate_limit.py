"""
Middleware для ограничения частоты запросов.
"""

import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from bot.config import config
from bot.locales import get_text


class RateLimitMiddleware(BaseMiddleware):
    """Middleware для rate limiting (защита от спама)."""
    
    def __init__(self):
        super().__init__()
        self.user_requests: Dict[int, list] = defaultdict(list)
        self.limit = config.RATE_LIMIT_MESSAGES
        self.period = config.RATE_LIMIT_PERIOD
    
    def _clean_old_requests(self, user_id: int) -> None:
        """Удаляем старые запросы за пределами периода."""
        current_time = time.time()
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < self.period
        ]
    
    def _is_rate_limited(self, user_id: int) -> bool:
        """Проверить, превышен ли лимит."""
        self._clean_old_requests(user_id)
        return len(self.user_requests[user_id]) >= self.limit
    
    def _add_request(self, user_id: int) -> None:
        """Добавить запрос."""
        self.user_requests[user_id].append(time.time())
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id: int | None = None
        
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
        
        if user_id is None:
            return await handler(event, data)
        
        # Админы не ограничены
        if user_id in config.ADMIN_IDS:
            return await handler(event, data)
        
        # Проверяем лимит
        if self._is_rate_limited(user_id):
            lang = data.get('lang', 'ru')
            text = get_text('rate_limit', lang)
            
            if isinstance(event, Message):
                await event.answer(text)
                return None
            elif isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
                return None
        
        # Добавляем запрос
        self._add_request(user_id)
        
        return await handler(event, data)
