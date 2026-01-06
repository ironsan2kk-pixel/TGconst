"""
Сервисы бота.
"""

from bot.services.notifications import notify_new_user, notify_admins


__all__ = [
    'notify_new_user',
    'notify_admins',
]
