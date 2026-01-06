"""
Pyrogram Userbot для управления каналами.

Функционал:
- Добавление пользователей в каналы
- Удаление пользователей из каналов
- Проверка участия в каналах
"""

from .config import userbot_config
from .client import userbot_client, get_userbot, UserbotClient

__all__ = [
    'userbot_config',
    'userbot_client',
    'get_userbot',
    'UserbotClient',
]
