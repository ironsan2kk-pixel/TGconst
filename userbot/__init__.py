"""
Userbot модуль

Предоставляет Pyrogram клиент для:
- Добавления пользователей в каналы
- Удаления пользователей из каналов
- Проверки участия в канале
"""

from .client import UserbotClient, get_userbot_client
from .config import UserbotSettings, get_settings

__all__ = [
    "UserbotClient",
    "get_userbot_client",
    "UserbotSettings",
    "get_settings"
]
