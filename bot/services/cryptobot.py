"""
CryptoBot API client для приёма криптовалютных платежей.

Документация: https://help.crypt.bot/crypto-pay-api
"""

import hashlib
import hmac
from datetime import datetime
from typing import Any

import httpx

from bot.config import config


class CryptoBotError(Exception):
    """Ошибка CryptoBot API."""
    pass


class CryptoBotAPI:
    """
    Клиент для работы с CryptoBot API.
    
    Поддерживает создание инвойсов, проверку статуса и верификацию вебхуков.
    """
    
    BASE_URL = "https://pay.crypt.bot/api"
    
    def __init__(self, token: str | None = None):
        """
        Инициализация клиента.
        
        Args:
            token: Токен CryptoBot API. Если не указан, берётся из конфига.
        """
        self.token = token or config.CRYPTOBOT_TOKEN
        self._client: httpx.AsyncClient | None = None
    
    @property
    def is_configured(self) -> bool:
        """Проверить, настроен ли CryptoBot."""
        return bool(self.token)
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Получить или создать HTTP клиент."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Crypto-Pay-API-Token": self.token,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client
    
    async def close(self) -> None:
        """Закрыть HTTP клиент."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Выполнить запрос к API.
        
        Args:
            method: HTTP метод (GET, POST)
            endpoint: Эндпоинт API
            data: Данные запроса
            
        Returns:
            Ответ API
            
        Raises:
            CryptoBotError: Ошибка API
        """
        client = await self._get_client()
        
        try:
            if method.upper() == "GET":
                response = await client.get(endpoint, params=data)
            else:
                response = await client.post(endpoint, json=data)
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                error = result.get("error", {})
                raise CryptoBotError(
                    f"CryptoBot API error: {error.get('code')} - {error.get('name')}"
                )
            
            return result.get("result", {})
            
        except httpx.HTTPStatusError as e:
            raise CryptoBotError(f"HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise CryptoBotError(f"Request error: {str(e)}") from e
    
    async def get_me(self) -> dict[str, Any]:
        """
        Получить информацию о приложении.
        
        Returns:
            Информация о приложении CryptoBot
        """
        return await self._request("GET", "/getMe")
    
    async def create_invoice(
        self,
        amount: float,
        currency: str = "USDT",
        description: str = "",
        payload: str = "",
        expires_in: int = 3600,  # 1 час
        allow_comments: bool = False,
        allow_anonymous: bool = True,
    ) -> dict[str, Any]:
        """
        Создать инвойс для оплаты.
        
        Args:
            amount: Сумма
            currency: Валюта (USDT, TON, BTC, ETH и др.)
            description: Описание платежа
            payload: Произвольные данные (до 1024 символов)
            expires_in: Время жизни инвойса в секундах
            allow_comments: Разрешить комментарии
            allow_anonymous: Разрешить анонимную оплату
            
        Returns:
            Данные созданного инвойса:
            - invoice_id: ID инвойса
            - status: Статус (active, paid, expired)
            - hash: Хеш для оплаты
            - bot_invoice_url: Ссылка на оплату
            - mini_app_invoice_url: Ссылка для Mini App
            - amount: Сумма
            - created_at: Дата создания
            - expiration_date: Дата истечения
        """
        data = {
            "currency_type": "crypto",
            "asset": currency,
            "amount": str(amount),
            "description": description[:1024] if description else "",
            "expires_in": expires_in,
            "allow_comments": allow_comments,
            "allow_anonymous": allow_anonymous,
        }
        
        if payload:
            data["payload"] = payload[:1024]
        
        return await self._request("POST", "/createInvoice", data)
    
    async def get_invoices(
        self,
        invoice_ids: list[int] | None = None,
        status: str | None = None,
        offset: int = 0,
        count: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Получить список инвойсов.
        
        Args:
            invoice_ids: Список ID инвойсов
            status: Фильтр по статусу (active, paid, expired)
            offset: Смещение
            count: Количество (макс. 1000)
            
        Returns:
            Список инвойсов
        """
        data = {
            "offset": offset,
            "count": min(count, 1000),
        }
        
        if invoice_ids:
            data["invoice_ids"] = ",".join(map(str, invoice_ids))
        
        if status:
            data["status"] = status
        
        result = await self._request("GET", "/getInvoices", data)
        return result.get("items", [])
    
    async def get_invoice(self, invoice_id: int | str) -> dict[str, Any] | None:
        """
        Получить информацию об инвойсе по ID.
        
        Args:
            invoice_id: ID инвойса
            
        Returns:
            Данные инвойса или None если не найден
        """
        invoices = await self.get_invoices(invoice_ids=[int(invoice_id)])
        return invoices[0] if invoices else None
    
    async def delete_invoice(self, invoice_id: int) -> bool:
        """
        Удалить инвойс.
        
        Args:
            invoice_id: ID инвойса
            
        Returns:
            True если успешно
        """
        result = await self._request("POST", "/deleteInvoice", {"invoice_id": invoice_id})
        return bool(result)
    
    @staticmethod
    def verify_webhook_signature(
        body: bytes,
        signature: str,
        token: str | None = None,
    ) -> bool:
        """
        Проверить подпись вебхука.
        
        Args:
            body: Тело запроса (bytes)
            signature: Подпись из заголовка crypto-pay-api-signature
            token: Токен API (если не указан, берётся из конфига)
            
        Returns:
            True если подпись верна
        """
        if not token:
            token = config.CRYPTOBOT_TOKEN
        
        if not token:
            return False
        
        # Создаём секретный ключ из токена
        secret = hashlib.sha256(token.encode()).digest()
        
        # Вычисляем HMAC-SHA256
        expected_signature = hmac.new(
            secret,
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def parse_webhook_payload(data: dict[str, Any]) -> dict[str, Any]:
        """
        Распарсить payload вебхука.
        
        Args:
            data: Данные вебхука
            
        Returns:
            Распаршенные данные:
            - update_type: Тип обновления
            - update_id: ID обновления
            - invoice: Данные инвойса (если есть)
        """
        return {
            "update_type": data.get("update_type"),
            "update_id": data.get("update_id"),
            "invoice": data.get("payload", {}),
        }


# Глобальный экземпляр
cryptobot = CryptoBotAPI()
