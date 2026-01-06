"""
Pyrogram Client для userbot.

Singleton клиент для работы с Telegram API.
"""

import asyncio
import logging
from typing import Optional

from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    UserNotParticipant,
    ChatAdminRequired,
    UserPrivacyRestricted,
    PeerIdInvalid,
    UserBannedInChannel,
    UserKicked,
    UserNotMutualContact,
    ChannelPrivate,
    InputUserDeactivated,
    UserDeactivated,
    UserDeactivatedBan,
)

from .config import userbot_config

logger = logging.getLogger(__name__)


class UserbotClient:
    """Singleton Pyrogram client."""
    
    _instance: Optional['UserbotClient'] = None
    _client: Optional[Client] = None
    _is_connected: bool = False
    
    def __new__(cls) -> 'UserbotClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._create_client()
    
    def _create_client(self) -> None:
        """Создать Pyrogram клиент."""
        if userbot_config.has_session_string():
            # Используем session string
            logger.info("Using session string for authentication")
            self._client = Client(
                name=userbot_config.SESSION_NAME,
                api_id=userbot_config.API_ID,
                api_hash=userbot_config.API_HASH,
                session_string=userbot_config.SESSION_STRING,
                in_memory=True,
            )
        else:
            # Используем файл сессии
            logger.info("Using session file for authentication")
            session_path = userbot_config.SESSION_DIR / userbot_config.SESSION_NAME
            self._client = Client(
                name=str(session_path),
                api_id=userbot_config.API_ID,
                api_hash=userbot_config.API_HASH,
                phone_number=userbot_config.PHONE,
            )
    
    @property
    def client(self) -> Client:
        """Получить клиент."""
        if self._client is None:
            self._create_client()
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Проверить подключение."""
        return self._is_connected and self._client is not None
    
    async def start(self) -> None:
        """Запустить клиент."""
        if self._is_connected:
            logger.warning("Client is already connected")
            return
        
        try:
            await self._client.start()
            self._is_connected = True
            me = await self._client.get_me()
            logger.info(f"Userbot started as @{me.username} ({me.id})")
        except Exception as e:
            logger.error(f"Failed to start userbot: {e}")
            raise
    
    async def stop(self) -> None:
        """Остановить клиент."""
        if not self._is_connected:
            return
        
        try:
            await self._client.stop()
            self._is_connected = False
            logger.info("Userbot stopped")
        except Exception as e:
            logger.error(f"Error stopping userbot: {e}")
    
    async def invite_user_to_channel(
        self,
        channel_id: int,
        user_id: int,
    ) -> tuple[bool, str]:
        """
        Добавить пользователя в канал.
        
        Args:
            channel_id: ID канала
            user_id: Telegram ID пользователя
            
        Returns:
            Tuple (успех, сообщение об ошибке)
        """
        if not self._is_connected:
            return False, "Userbot not connected"
        
        try:
            await self._client.add_chat_members(
                chat_id=channel_id,
                user_ids=user_id,
            )
            logger.info(f"User {user_id} added to channel {channel_id}")
            return True, ""
            
        except FloodWait as e:
            logger.warning(f"FloodWait: waiting {e.value} seconds")
            await asyncio.sleep(e.value)
            # Попробуем ещё раз
            return await self.invite_user_to_channel(channel_id, user_id)
        
        except UserPrivacyRestricted:
            msg = "User privacy settings prevent adding"
            logger.warning(f"User {user_id}: {msg}")
            return False, msg
        
        except ChatAdminRequired:
            msg = "Bot is not admin in channel"
            logger.error(f"Channel {channel_id}: {msg}")
            return False, msg
        
        except PeerIdInvalid:
            msg = "Invalid user or channel ID"
            logger.error(f"User {user_id}, Channel {channel_id}: {msg}")
            return False, msg
        
        except UserBannedInChannel:
            msg = "User is banned in channel"
            logger.warning(f"User {user_id}: {msg}")
            return False, msg
        
        except UserNotMutualContact:
            msg = "User must be mutual contact"
            logger.warning(f"User {user_id}: {msg}")
            return False, msg
        
        except ChannelPrivate:
            msg = "Channel is private, cannot access"
            logger.error(f"Channel {channel_id}: {msg}")
            return False, msg
        
        except (InputUserDeactivated, UserDeactivated, UserDeactivatedBan):
            msg = "User account is deactivated"
            logger.warning(f"User {user_id}: {msg}")
            return False, msg
        
        except Exception as e:
            msg = str(e)
            logger.error(f"Error inviting user {user_id} to channel {channel_id}: {msg}")
            return False, msg
    
    async def kick_user_from_channel(
        self,
        channel_id: int,
        user_id: int,
    ) -> tuple[bool, str]:
        """
        Удалить пользователя из канала.
        
        Args:
            channel_id: ID канала
            user_id: Telegram ID пользователя
            
        Returns:
            Tuple (успех, сообщение об ошибке)
        """
        if not self._is_connected:
            return False, "Userbot not connected"
        
        try:
            await self._client.ban_chat_member(
                chat_id=channel_id,
                user_id=user_id,
            )
            # Сразу разбаним, чтобы можно было добавить снова
            await asyncio.sleep(0.5)
            await self._client.unban_chat_member(
                chat_id=channel_id,
                user_id=user_id,
            )
            logger.info(f"User {user_id} kicked from channel {channel_id}")
            return True, ""
            
        except FloodWait as e:
            logger.warning(f"FloodWait: waiting {e.value} seconds")
            await asyncio.sleep(e.value)
            return await self.kick_user_from_channel(channel_id, user_id)
        
        except UserNotParticipant:
            msg = "User is not in channel"
            logger.info(f"User {user_id}: {msg}")
            return True, ""  # Считаем успехом, если юзера и так нет
        
        except ChatAdminRequired:
            msg = "Bot is not admin in channel"
            logger.error(f"Channel {channel_id}: {msg}")
            return False, msg
        
        except PeerIdInvalid:
            msg = "Invalid user or channel ID"
            logger.error(f"User {user_id}, Channel {channel_id}: {msg}")
            return False, msg
        
        except ChannelPrivate:
            msg = "Channel is private, cannot access"
            logger.error(f"Channel {channel_id}: {msg}")
            return False, msg
        
        except UserKicked:
            msg = "User already kicked"
            logger.info(f"User {user_id}: {msg}")
            return True, ""
        
        except Exception as e:
            msg = str(e)
            logger.error(f"Error kicking user {user_id} from channel {channel_id}: {msg}")
            return False, msg
    
    async def check_user_in_channel(
        self,
        channel_id: int,
        user_id: int,
    ) -> bool:
        """
        Проверить, находится ли пользователь в канале.
        
        Args:
            channel_id: ID канала
            user_id: Telegram ID пользователя
            
        Returns:
            True если пользователь в канале
        """
        if not self._is_connected:
            return False
        
        try:
            member = await self._client.get_chat_member(
                chat_id=channel_id,
                user_id=user_id,
            )
            # Проверяем статус участника
            return member.status.value not in ['left', 'banned', 'kicked']
        
        except UserNotParticipant:
            return False
        
        except Exception as e:
            logger.error(f"Error checking user {user_id} in channel {channel_id}: {e}")
            return False
    
    async def get_session_string(self) -> str:
        """Получить session string для сохранения."""
        if not self._is_connected:
            raise RuntimeError("Client is not connected")
        return await self._client.export_session_string()


# Глобальный экземпляр
userbot_client = UserbotClient()


async def get_userbot() -> UserbotClient:
    """Получить экземпляр userbot клиента."""
    if not userbot_client.is_connected:
        await userbot_client.start()
    return userbot_client
