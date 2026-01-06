"""
Webhook эндпоинты для обработки callback от CryptoBot
"""

from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select
import logging

from ..services.cryptobot import CryptoBotAPI
from ..services.userbot import get_userbot_service
from ..database import get_main_db, get_bot_db
from ..models.main_db import Bot
from ..models.bot_db import Payment, Subscription, User, Tariff, Channel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class CryptoBotWebhookPayload(BaseModel):
    """Payload от CryptoBot webhook"""
    update_id: int
    update_type: str  # invoice_paid
    request_date: datetime
    payload: Optional[str] = None
    
    # Invoice данные
    invoice_id: Optional[int] = None
    hash: Optional[str] = None
    currency_type: Optional[str] = None
    asset: Optional[str] = None
    amount: Optional[str] = None
    paid_asset: Optional[str] = None
    paid_amount: Optional[str] = None
    paid_fiat_rate: Optional[str] = None
    accepted_assets: Optional[list] = None
    fee_asset: Optional[str] = None
    fee_amount: Optional[str] = None
    fee: Optional[str] = None
    pay_url: Optional[str] = None
    bot_invoice_url: Optional[str] = None
    mini_app_invoice_url: Optional[str] = None
    web_app_invoice_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    allow_comments: Optional[bool] = None
    allow_anonymous: Optional[bool] = None
    expiration_date: Optional[datetime] = None
    paid_anonymously: Optional[bool] = None
    comment: Optional[str] = None
    hidden_message: Optional[str] = None
    paid_btn_name: Optional[str] = None
    paid_btn_url: Optional[str] = None


async def process_payment(bot_uuid: str, invoice_id: int, paid_at: datetime, payload_data: str):
    """
    Обработка успешной оплаты
    
    Args:
        bot_uuid: UUID бота
        invoice_id: ID инвойса
        paid_at: Дата оплаты
        payload_data: Данные из payload (формат: user_id:tariff_id[:promocode_id])
    """
    try:
        # Парсим payload
        parts = payload_data.split(":")
        if len(parts) < 2:
            logger.error(f"Invalid payload format: {payload_data}")
            return
        
        user_id = int(parts[0])
        tariff_id = int(parts[1])
        promocode_id = int(parts[2]) if len(parts) > 2 and parts[2] else None
        
        # Получаем сессию БД бота
        async for session in get_bot_db(bot_uuid):
            # Находим платёж по invoice_id
            stmt = select(Payment).where(Payment.invoice_id == str(invoice_id))
            result = await session.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if not payment:
                logger.error(f"Payment not found for invoice_id: {invoice_id}")
                return
            
            if payment.status == "paid":
                logger.info(f"Payment {invoice_id} already processed")
                return
            
            # Обновляем статус платежа
            payment.status = "paid"
            payment.paid_at = paid_at
            
            # Получаем тариф
            stmt = select(Tariff).where(Tariff.id == tariff_id)
            result = await session.execute(stmt)
            tariff = result.scalar_one_or_none()
            
            if not tariff:
                logger.error(f"Tariff not found: {tariff_id}")
                return
            
            # Получаем пользователя
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User not found: {user_id}")
                return
            
            # Создаём подписку
            starts_at = datetime.utcnow()
            expires_at = starts_at + timedelta(days=tariff.duration_days)
            
            subscription = Subscription(
                user_id=user.id,
                channel_id=tariff.channel_id,
                tariff_id=tariff.id,
                starts_at=starts_at,
                expires_at=expires_at,
                is_active=True,
                auto_kicked=False
            )
            session.add(subscription)
            
            # Обновляем payment с subscription_id после flush
            await session.flush()
            payment.subscription_id = subscription.id
            
            await session.commit()
            
            logger.info(f"Payment {invoice_id} processed successfully. Subscription created for user {user.telegram_id}")
            
            # Отправляем задачу на добавление в канал
            await notify_userbot_invite(
                bot_uuid=bot_uuid,
                user_telegram_id=user.telegram_id,
                channel_id=tariff.channel_id,
                subscription_id=subscription.id
            )
            break  # Выходим из async for после обработки
            
    except Exception as e:
        logger.exception(f"Error processing payment: {e}")


async def notify_userbot_invite(bot_uuid: str, user_telegram_id: int, channel_id: int, subscription_id: int):
    """
    Уведомить userbot о необходимости добавить пользователя в канал
    
    Args:
        bot_uuid: UUID бота
        user_telegram_id: Telegram ID пользователя
        channel_id: ID канала в БД бота (не telegram channel_id!)
        subscription_id: ID подписки
    """
    logger.info(
        f"Отправка задачи invite: user={user_telegram_id}, "
        f"channel={channel_id}, subscription={subscription_id}"
    )
    
    userbot_service = get_userbot_service()
    
    result = await userbot_service.invite_user(
        bot_uuid=bot_uuid,
        user_telegram_id=user_telegram_id,
        channel_id=channel_id,
        subscription_id=subscription_id,
        sync=False  # Асинхронно
    )
    
    if result["success"]:
        logger.info(f"Задача invite отправлена успешно: task_id={result.get('task_id')}")
    else:
        logger.error(f"Ошибка отправки задачи invite: {result.get('error')}")


async def notify_userbot_kick(bot_uuid: str, user_telegram_id: int, channel_id: int, subscription_id: int):
    """
    Уведомить userbot о необходимости удалить пользователя из канала
    
    Args:
        bot_uuid: UUID бота
        user_telegram_id: Telegram ID пользователя
        channel_id: ID канала в БД бота
        subscription_id: ID подписки
    """
    logger.info(
        f"Отправка задачи kick: user={user_telegram_id}, "
        f"channel={channel_id}, subscription={subscription_id}"
    )
    
    userbot_service = get_userbot_service()
    
    result = await userbot_service.kick_user(
        bot_uuid=bot_uuid,
        user_telegram_id=user_telegram_id,
        channel_id=channel_id,
        subscription_id=subscription_id,
        sync=False
    )
    
    if result["success"]:
        logger.info(f"Задача kick отправлена успешно")
    else:
        logger.error(f"Ошибка отправки задачи kick: {result.get('error')}")


async def send_payment_notification(bot_uuid: str, user_telegram_id: int, tariff_name: str, expires_at: datetime):
    """
    Отправить уведомление об успешной оплате через бота
    """
    pass  # Реализуется через бота


@router.post("/cryptobot/{bot_uuid}")
async def cryptobot_webhook(
    bot_uuid: str,
    request: Request,
    background_tasks: BackgroundTasks,
    crypto_pay_api_signature: Optional[str] = Header(None, alias="crypto-pay-api-signature")
):
    """
    Webhook эндпоинт для CryptoBot
    
    CryptoBot отправляет POST запрос с подписью при оплате инвойса
    """
    # Получаем тело запроса
    body = await request.body()
    
    # Получаем бота из БД для проверки токена
    cryptobot_token = None
    async for session in get_main_db():
        stmt = select(Bot).where(Bot.uuid == bot_uuid)
        result = await session.execute(stmt)
        bot = result.scalar_one_or_none()
        
        if not bot:
            logger.warning(f"Bot not found: {bot_uuid}")
            raise HTTPException(status_code=404, detail="Bot not found")
        
        if not bot.cryptobot_token:
            logger.warning(f"CryptoBot token not configured for bot: {bot_uuid}")
            raise HTTPException(status_code=400, detail="CryptoBot not configured")
        
        cryptobot_token = bot.cryptobot_token
        break
    
    # Проверяем подпись
    if crypto_pay_api_signature:
        is_valid = CryptoBotAPI.verify_webhook_signature(
            token=cryptobot_token,
            body=body,
            signature=crypto_pay_api_signature
        )
        
        if not is_valid:
            logger.warning(f"Invalid webhook signature for bot: {bot_uuid}")
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        logger.warning(f"Missing webhook signature for bot: {bot_uuid}")
        # В продакшене нужно отклонять запросы без подписи
        # raise HTTPException(status_code=401, detail="Missing signature")
    
    # Парсим данные
    try:
        data = await request.json()
        logger.info(f"CryptoBot webhook received: {data}")
    except Exception as e:
        logger.error(f"Failed to parse webhook body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Проверяем тип события
    update_type = data.get("update_type")
    
    if update_type == "invoice_paid":
        # Получаем данные об оплаченном инвойсе
        payload_obj = data.get("payload", {})
        
        if isinstance(payload_obj, dict):
            invoice_id = payload_obj.get("invoice_id")
            paid_at_str = payload_obj.get("paid_at")
            payload_data = payload_obj.get("payload", "")
        else:
            invoice_id = data.get("invoice_id")
            paid_at_str = data.get("paid_at")
            payload_data = str(payload_obj) if payload_obj else ""
        
        paid_at = datetime.fromisoformat(paid_at_str.replace("Z", "+00:00")) if paid_at_str else datetime.utcnow()
        
        # Обрабатываем платёж в фоне
        background_tasks.add_task(
            process_payment,
            bot_uuid=bot_uuid,
            invoice_id=invoice_id,
            paid_at=paid_at,
            payload_data=payload_data
        )
    
    return {"ok": True}


@router.get("/cryptobot/{bot_uuid}/test")
async def test_cryptobot_connection(bot_uuid: str):
    """Тестовый эндпоинт для проверки подключения к CryptoBot"""
    async for session in get_main_db():
        stmt = select(Bot).where(Bot.uuid == bot_uuid)
        result = await session.execute(stmt)
        bot = result.scalar_one_or_none()
        
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        if not bot.cryptobot_token:
            raise HTTPException(status_code=400, detail="CryptoBot token not configured")
        
        try:
            api = CryptoBotAPI(bot.cryptobot_token)
            me = await api.get_me()
            return {
                "ok": True,
                "app_id": me.get("app_id"),
                "name": me.get("name"),
                "payment_processing_bot_username": me.get("payment_processing_bot_username")
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/userbot/health")
async def userbot_health():
    """Проверка состояния Userbot API"""
    userbot_service = get_userbot_service()
    result = await userbot_service.health_check()
    return result


@router.post("/userbot/reconnect")
async def userbot_reconnect():
    """Переподключить userbot"""
    userbot_service = get_userbot_service()
    result = await userbot_service.reconnect()
    return result
