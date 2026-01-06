"""
Middleware для бота.
"""

from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.user import UserMiddleware
from bot.middlewares.i18n import I18nMiddleware
from bot.middlewares.ban import BanMiddleware
from bot.middlewares.rate_limit import RateLimitMiddleware


__all__ = [
    'DatabaseMiddleware',
    'UserMiddleware',
    'I18nMiddleware',
    'BanMiddleware',
    'RateLimitMiddleware',
]
