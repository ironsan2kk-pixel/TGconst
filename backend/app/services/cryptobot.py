"""
CryptoBot API Client
Документация: https://help.crypt.bot/crypto-pay-api
"""

import httpx
import hashlib
import hmac
from typing import Optional, List
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class CryptoCurrency(str, Enum):
    USDT = "USDT"
    TON = "TON"
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    BNB = "BNB"
    TRX = "TRX"
    USDC = "USDC"


class InvoiceStatus(str, Enum):
    ACTIVE = "active"
    PAID = "paid"
    EXPIRED = "expired"


class Invoice(BaseModel):
    invoice_id: int
    hash: str
    currency_type: str
    asset: Optional[str] = None
    amount: str
    pay_url: str
    bot_invoice_url: str
    mini_app_invoice_url: str
    web_app_invoice_url: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None
    allow_comments: bool
    allow_anonymous: bool
    expiration_date: Optional[datetime] = None
    paid_anonymously: Optional[bool] = None
    comment: Optional[str] = None
    hidden_message: Optional[str] = None
    payload: Optional[str] = None
    paid_btn_name: Optional[str] = None
    paid_btn_url: Optional[str] = None


class CryptoBotAPI:
    """Клиент для работы с CryptoBot API"""
    
    BASE_URL = "https://pay.crypt.bot/api"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Crypto-Pay-API-Token": token,
            "Content-Type": "application/json"
        }
    
    async def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Выполнение запроса к API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=self.headers, params=data)
            else:
                response = await client.post(url, headers=self.headers, json=data)
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                error = result.get("error", {})
                raise CryptoBotError(
                    code=error.get("code", 0),
                    name=error.get("name", "Unknown"),
                    message=str(error)
                )
            
            return result.get("result")
    
    async def get_me(self) -> dict:
        """Получить информацию о приложении"""
        return await self._request("GET", "getMe")
    
    async def create_invoice(
        self,
        amount: float,
        currency_type: str = "crypto",
        asset: str = "USDT",
        description: Optional[str] = None,
        hidden_message: Optional[str] = None,
        paid_btn_name: Optional[str] = None,
        paid_btn_url: Optional[str] = None,
        payload: Optional[str] = None,
        allow_comments: bool = True,
        allow_anonymous: bool = True,
        expires_in: Optional[int] = None
    ) -> Invoice:
        """
        Создать инвойс для оплаты
        
        Args:
            amount: Сумма к оплате
            currency_type: Тип валюты (crypto/fiat)
            asset: Криптовалюта (USDT, TON, BTC и т.д.)
            description: Описание платежа
            hidden_message: Сообщение после оплаты
            paid_btn_name: Название кнопки после оплаты (viewItem, openChannel, openBot, callback)
            paid_btn_url: URL кнопки после оплаты
            payload: Произвольные данные (до 4096 символов)
            allow_comments: Разрешить комментарии
            allow_anonymous: Разрешить анонимную оплату
            expires_in: Время жизни инвойса в секундах (1-2678400)
        
        Returns:
            Invoice: Объект инвойса
        """
        data = {
            "currency_type": currency_type,
            "asset": asset,
            "amount": str(amount),
            "allow_comments": allow_comments,
            "allow_anonymous": allow_anonymous
        }
        
        if description:
            data["description"] = description[:1024]  # Макс 1024 символа
        
        if hidden_message:
            data["hidden_message"] = hidden_message[:2048]
        
        if paid_btn_name and paid_btn_url:
            data["paid_btn_name"] = paid_btn_name
            data["paid_btn_url"] = paid_btn_url
        
        if payload:
            data["payload"] = payload[:4096]
        
        if expires_in:
            data["expires_in"] = min(max(expires_in, 1), 2678400)  # 1 сек - 31 день
        
        result = await self._request("POST", "createInvoice", data)
        return Invoice(**result)
    
    async def get_invoices(
        self,
        asset: Optional[str] = None,
        invoice_ids: Optional[List[int]] = None,
        status: Optional[str] = None,
        offset: int = 0,
        count: int = 100
    ) -> List[Invoice]:
        """
        Получить список инвойсов
        
        Args:
            asset: Фильтр по криптовалюте
            invoice_ids: Список ID инвойсов
            status: Фильтр по статусу (active, paid, expired)
            offset: Смещение
            count: Количество (макс 1000)
        
        Returns:
            List[Invoice]: Список инвойсов
        """
        data = {
            "offset": offset,
            "count": min(count, 1000)
        }
        
        if asset:
            data["asset"] = asset
        
        if invoice_ids:
            data["invoice_ids"] = ",".join(map(str, invoice_ids))
        
        if status:
            data["status"] = status
        
        result = await self._request("GET", "getInvoices", data)
        items = result.get("items", [])
        return [Invoice(**item) for item in items]
    
    async def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Получить инвойс по ID"""
        invoices = await self.get_invoices(invoice_ids=[invoice_id])
        return invoices[0] if invoices else None
    
    async def delete_invoice(self, invoice_id: int) -> bool:
        """Удалить инвойс"""
        result = await self._request("POST", "deleteInvoice", {"invoice_id": invoice_id})
        return result is True
    
    async def get_balance(self) -> List[dict]:
        """Получить баланс"""
        return await self._request("GET", "getBalance")
    
    async def get_exchange_rates(self) -> List[dict]:
        """Получить курсы обмена"""
        return await self._request("GET", "getExchangeRates")
    
    async def get_currencies(self) -> List[dict]:
        """Получить список поддерживаемых валют"""
        return await self._request("GET", "getCurrencies")
    
    @staticmethod
    def verify_webhook_signature(token: str, body: bytes, signature: str) -> bool:
        """
        Проверить подпись webhook
        
        Args:
            token: CryptoBot API токен
            body: Тело запроса (bytes)
            signature: Значение заголовка crypto-pay-api-signature
        
        Returns:
            bool: True если подпись валидна
        """
        # Создаём секретный ключ из токена
        secret = hashlib.sha256(token.encode()).digest()
        
        # Вычисляем HMAC-SHA256
        expected_signature = hmac.new(
            secret,
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)


class CryptoBotError(Exception):
    """Исключение CryptoBot API"""
    
    def __init__(self, code: int, name: str, message: str):
        self.code = code
        self.name = name
        self.message = message
        super().__init__(f"CryptoBot API Error [{code}] {name}: {message}")
