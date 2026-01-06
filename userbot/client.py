"""
Pyrogram клиент для Userbot
"""

import asyncio
import logging
from typing import Optional
from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    UserPrivacyRestricted,
    UserNotMutualContact,
    UserChannelsTooMuch,
    ChatAdminRequired,
    ChannelPrivate,
    PeerIdInvalid,
    UserAlreadyParticipant,
    InviteHashExpired,
    UserBannedInChannel,
    SessionPasswordNeeded
)

from config import get_settings

logger = logging.getLogger(__name__)


class UserbotClient:
    """Обёртка над Pyrogram Client"""
    
    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[Client] = None
        self._is_connected = False
        self._lock = asyncio.Lock()
    
    @property
    def client(self) -> Optional[Client]:
        """Получить клиент"""
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Проверка подключения"""
        return self._is_connected and self._client is not None
    
    async def connect(self) -> bool:
        """
        Подключить клиент к Telegram
        
        Returns:
            True если подключение успешно
        """
        async with self._lock:
            if self._is_connected:
                return True
            
            if not self.settings.is_configured:
                logger.error("Userbot не настроен. Проверьте USERBOT_API_ID, USERBOT_API_HASH")
                return False
            
            try:
                # Создаём клиент
                if self.settings.USERBOT_SESSION_STRING:
                    # Используем session_string (рекомендуется для продакшена)
                    self._client = Client(
                        name="userbot",
                        api_id=self.settings.USERBOT_API_ID,
                        api_hash=self.settings.USERBOT_API_HASH,
                        session_string=self.settings.USERBOT_SESSION_STRING,
                        in_memory=True
                    )
                else:
                    # Используем phone (нужна интерактивная авторизация)
                    self._client = Client(
                        name="userbot",
                        api_id=self.settings.USERBOT_API_ID,
                        api_hash=self.settings.USERBOT_API_HASH,
                        phone_number=self.settings.USERBOT_PHONE,
                        workdir=str(self.settings.DATA_DIR)
                    )
                
                await self._client.start()
                
                me = await self._client.get_me()
                logger.info(f"Userbot подключен как: {me.first_name} (@{me.username})")
                
                self._is_connected = True
                return True
                
            except SessionPasswordNeeded:
                logger.error("Требуется 2FA пароль. Используйте session_string.")
                return False
            except Exception as e:
                logger.exception(f"Ошибка подключения userbot: {e}")
                return False
    
    async def disconnect(self):
        """Отключить клиент"""
        async with self._lock:
            if self._client and self._is_connected:
                try:
                    await self._client.stop()
                except Exception as e:
                    logger.error(f"Ошибка отключения: {e}")
                finally:
                    self._is_connected = False
                    self._client = None
    
    async def get_me(self) -> Optional[dict]:
        """Получить информацию о текущем пользователе"""
        if not self.is_connected:
            return None
        
        try:
            me = await self._client.get_me()
            return {
                "id": me.id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "phone_number": me.phone_number
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            return None
    
    async def invite_user_to_channel(
        self, 
        user_id: int, 
        channel_id: int
    ) -> dict:
        """
        Добавить пользователя в канал/группу
        
        Args:
            user_id: Telegram ID пользователя
            channel_id: Telegram ID канала (со знаком минус для супергрупп/каналов)
        
        Returns:
            {
                "success": bool,
                "error": str или None,
                "error_type": str или None,
                "retry_after": int или None (для FloodWait)
            }
        """
        if not self.is_connected:
            return {
                "success": False,
                "error": "Userbot не подключен",
                "error_type": "not_connected",
                "retry_after": None
            }
        
        try:
            # Пытаемся добавить пользователя
            await self._client.add_chat_members(
                chat_id=channel_id,
                user_ids=user_id
            )
            
            logger.info(f"Пользователь {user_id} добавлен в канал {channel_id}")
            return {
                "success": True,
                "error": None,
                "error_type": None,
                "retry_after": None
            }
        
        except UserAlreadyParticipant:
            logger.info(f"Пользователь {user_id} уже в канале {channel_id}")
            return {
                "success": True,  # Считаем успехом
                "error": None,
                "error_type": "already_participant",
                "retry_after": None
            }
        
        except FloodWait as e:
            logger.warning(f"FloodWait: ждать {e.value} секунд")
            return {
                "success": False,
                "error": f"Слишком много запросов. Ждать {e.value} сек.",
                "error_type": "flood_wait",
                "retry_after": e.value
            }
        
        except UserPrivacyRestricted:
            logger.warning(f"Пользователь {user_id} запретил добавление в группы")
            return {
                "success": False,
                "error": "Пользователь запретил добавление в группы",
                "error_type": "privacy_restricted",
                "retry_after": None
            }
        
        except UserNotMutualContact:
            logger.warning(f"Пользователь {user_id} не является контактом")
            return {
                "success": False,
                "error": "Пользователь не является контактом",
                "error_type": "not_mutual_contact",
                "retry_after": None
            }
        
        except UserChannelsTooMuch:
            logger.warning(f"Пользователь {user_id} в слишком многих каналах")
            return {
                "success": False,
                "error": "Пользователь достиг лимита каналов/групп",
                "error_type": "channels_too_much",
                "retry_after": None
            }
        
        except ChatAdminRequired:
            logger.error(f"Нужны права админа в канале {channel_id}")
            return {
                "success": False,
                "error": "Userbot не является админом канала",
                "error_type": "admin_required",
                "retry_after": None
            }
        
        except ChannelPrivate:
            logger.error(f"Канал {channel_id} приватный или недоступен")
            return {
                "success": False,
                "error": "Канал приватный или недоступен",
                "error_type": "channel_private",
                "retry_after": None
            }
        
        except PeerIdInvalid:
            logger.error(f"Неверный ID пользователя {user_id} или канала {channel_id}")
            return {
                "success": False,
                "error": "Неверный ID пользователя или канала",
                "error_type": "peer_id_invalid",
                "retry_after": None
            }
        
        except UserBannedInChannel:
            logger.warning(f"Пользователь {user_id} забанен в канале {channel_id}")
            return {
                "success": False,
                "error": "Пользователь забанен в канале",
                "error_type": "user_banned",
                "retry_after": None
            }
        
        except InviteHashExpired:
            logger.error(f"Ссылка-приглашение истекла для канала {channel_id}")
            return {
                "success": False,
                "error": "Ссылка-приглашение истекла",
                "error_type": "invite_expired",
                "retry_after": None
            }
        
        except Exception as e:
            logger.exception(f"Неизвестная ошибка при добавлении: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "unknown",
                "retry_after": None
            }
    
    async def kick_user_from_channel(
        self, 
        user_id: int, 
        channel_id: int
    ) -> dict:
        """
        Удалить пользователя из канала/группы
        
        Args:
            user_id: Telegram ID пользователя
            channel_id: Telegram ID канала
        
        Returns:
            {
                "success": bool,
                "error": str или None,
                "error_type": str или None
            }
        """
        if not self.is_connected:
            return {
                "success": False,
                "error": "Userbot не подключен",
                "error_type": "not_connected"
            }
        
        try:
            await self._client.ban_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )
            
            # Сразу разбаниваем, чтобы пользователь мог вернуться после оплаты
            await self._client.unban_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )
            
            logger.info(f"Пользователь {user_id} удалён из канала {channel_id}")
            return {
                "success": True,
                "error": None,
                "error_type": None
            }
        
        except FloodWait as e:
            logger.warning(f"FloodWait: ждать {e.value} секунд")
            return {
                "success": False,
                "error": f"Слишком много запросов. Ждать {e.value} сек.",
                "error_type": "flood_wait"
            }
        
        except ChatAdminRequired:
            logger.error(f"Нужны права админа в канале {channel_id}")
            return {
                "success": False,
                "error": "Userbot не является админом канала",
                "error_type": "admin_required"
            }
        
        except Exception as e:
            logger.exception(f"Ошибка при удалении пользователя: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "unknown"
            }
    
    async def get_channel_info(self, channel_id: int) -> Optional[dict]:
        """Получить информацию о канале"""
        if not self.is_connected:
            return None
        
        try:
            chat = await self._client.get_chat(channel_id)
            return {
                "id": chat.id,
                "title": chat.title,
                "username": chat.username,
                "type": str(chat.type),
                "members_count": chat.members_count
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о канале: {e}")
            return None
    
    async def check_user_in_channel(self, user_id: int, channel_id: int) -> Optional[bool]:
        """
        Проверить, является ли пользователь участником канала
        
        Returns:
            True - пользователь в канале
            False - пользователь не в канале
            None - ошибка проверки
        """
        if not self.is_connected:
            return None
        
        try:
            member = await self._client.get_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )
            # Статусы: owner, administrator, member, restricted, left, banned
            return member.status.value in ["owner", "administrator", "member", "restricted"]
        except Exception as e:
            logger.error(f"Ошибка проверки участника: {e}")
            return None


# Глобальный экземпляр клиента
_userbot_client: Optional[UserbotClient] = None


def get_userbot_client() -> UserbotClient:
    """Получить глобальный экземпляр userbot клиента"""
    global _userbot_client
    if _userbot_client is None:
        _userbot_client = UserbotClient()
    return _userbot_client
