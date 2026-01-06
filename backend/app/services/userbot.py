"""
Сервис для взаимодействия с Userbot API
"""

import logging
from typing import Optional
import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


def get_userbot_api_url() -> str:
    """Получить URL Userbot API из настроек"""
    settings = get_settings()
    return f"http://{settings.USERBOT_HOST}:{settings.USERBOT_PORT}"


class UserbotService:
    """Клиент для работы с Userbot API"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or get_userbot_api_url()).rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Получить HTTP клиент"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
        return self._client
    
    async def close(self):
        """Закрыть клиент"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def health_check(self) -> dict:
        """
        Проверка состояния userbot
        
        Returns:
            {"status": "ok", "userbot_connected": bool, "userbot_info": dict}
        """
        try:
            client = await self._get_client()
            response = await client.get("/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка проверки userbot: {e}")
            return {
                "status": "error",
                "userbot_connected": False,
                "error": str(e)
            }
    
    async def invite_user(
        self,
        bot_uuid: str,
        user_telegram_id: int,
        channel_id: int,
        subscription_id: int,
        sync: bool = False
    ) -> dict:
        """
        Отправить задачу на добавление пользователя в канал
        
        Args:
            bot_uuid: UUID бота
            user_telegram_id: Telegram ID пользователя
            channel_id: ID канала в БД бота
            subscription_id: ID подписки
            sync: Ждать результата (True) или выполнить в фоне (False)
        
        Returns:
            {"success": bool, "error": str?, "task_id": str?}
        """
        try:
            client = await self._get_client()
            
            endpoint = "/invite/sync" if sync else "/invite"
            
            response = await client.post(
                endpoint,
                json={
                    "bot_uuid": bot_uuid,
                    "user_telegram_id": user_telegram_id,
                    "channel_id": channel_id,
                    "subscription_id": subscription_id
                }
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.ConnectError:
            logger.error("Не удалось подключиться к Userbot API. Убедитесь что userbot запущен.")
            return {
                "success": False,
                "error": "Userbot API недоступен"
            }
        except Exception as e:
            logger.exception(f"Ошибка при отправке задачи invite: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def kick_user(
        self,
        bot_uuid: str,
        user_telegram_id: int,
        channel_id: int,
        subscription_id: int,
        sync: bool = False
    ) -> dict:
        """
        Отправить задачу на удаление пользователя из канала
        
        Args:
            bot_uuid: UUID бота
            user_telegram_id: Telegram ID пользователя
            channel_id: ID канала в БД бота
            subscription_id: ID подписки
            sync: Ждать результата (True) или выполнить в фоне (False)
        
        Returns:
            {"success": bool, "error": str?}
        """
        try:
            client = await self._get_client()
            
            endpoint = "/kick/sync" if sync else "/kick"
            
            response = await client.post(
                endpoint,
                json={
                    "bot_uuid": bot_uuid,
                    "user_telegram_id": user_telegram_id,
                    "channel_id": channel_id,
                    "subscription_id": subscription_id
                }
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.ConnectError:
            logger.error("Не удалось подключиться к Userbot API")
            return {
                "success": False,
                "error": "Userbot API недоступен"
            }
        except Exception as e:
            logger.exception(f"Ошибка при отправке задачи kick: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_channel_info(self, channel_id: int) -> Optional[dict]:
        """Получить информацию о канале через userbot"""
        try:
            client = await self._get_client()
            response = await client.get(f"/channel/{channel_id}")
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о канале: {e}")
            return None
    
    async def check_user_in_channel(self, channel_id: int, user_id: int) -> Optional[bool]:
        """Проверить, находится ли пользователь в канале"""
        try:
            client = await self._get_client()
            response = await client.get(f"/check/{channel_id}/{user_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("is_member")
            
        except Exception as e:
            logger.error(f"Ошибка проверки пользователя в канале: {e}")
            return None
    
    async def reconnect(self) -> dict:
        """Переподключить userbot"""
        try:
            client = await self._get_client()
            response = await client.post("/reconnect")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка переподключения userbot: {e}")
            return {"success": False, "error": str(e)}


# Глобальный экземпляр сервиса
_userbot_service: Optional[UserbotService] = None


def get_userbot_service() -> UserbotService:
    """Получить глобальный экземпляр сервиса"""
    global _userbot_service
    if _userbot_service is None:
        _userbot_service = UserbotService()
    return _userbot_service
