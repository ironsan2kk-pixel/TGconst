"""
Сервис проверки подписок и автокика

Функционал:
- Фоновая задача проверки каждые 5 минут
- Уведомление пользователей за 1 день до истечения
- Автокик через userbot при истечении
- Обновление статусов подписок в БД
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

import httpx
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ..config import get_settings
from ..models.bot_db import Subscription, User, Channel
from ..models.main_db import Bot
from .userbot import get_userbot_service

logger = logging.getLogger(__name__)

# Настройки проверки
CHECK_INTERVAL_SECONDS = 300  # 5 минут
NOTIFY_BEFORE_DAYS = 1  # Уведомлять за 1 день до истечения
BATCH_SIZE = 50  # Размер пакета для обработки


class SubscriptionChecker:
    """Сервис проверки подписок"""
    
    def __init__(self):
        self.settings = get_settings()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._userbot_service = get_userbot_service()
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    async def start(self):
        """Запустить фоновую проверку"""
        if self._running:
            logger.warning("Subscription checker уже запущен")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._check_loop())
        logger.info("✅ Subscription checker запущен")
    
    async def stop(self):
        """Остановить фоновую проверку"""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        logger.info("🛑 Subscription checker остановлен")
    
    async def _check_loop(self):
        """Основной цикл проверки"""
        logger.info(f"Subscription checker: проверка каждые {CHECK_INTERVAL_SECONDS} секунд")
        
        while self._running:
            try:
                await self._run_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Ошибка в цикле проверки подписок: {e}")
            
            # Ждём до следующей проверки
            try:
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
    
    async def _run_check(self):
        """Выполнить одну проверку всех ботов"""
        logger.debug("Начинаем проверку подписок...")
        
        # Получаем список активных ботов
        bots = await self._get_active_bots()
        
        if not bots:
            logger.debug("Нет активных ботов для проверки")
            return
        
        total_expired = 0
        total_notified = 0
        
        for bot in bots:
            try:
                result = await self._check_bot_subscriptions(bot)
                total_expired += result.get("expired_kicked", 0)
                total_notified += result.get("expiring_notified", 0)
            except Exception as e:
                logger.error(f"Ошибка проверки бота {bot['uuid']}: {e}")
        
        if total_expired > 0 or total_notified > 0:
            logger.info(
                f"Проверка завершена: "
                f"кикнуто={total_expired}, уведомлено={total_notified}"
            )
    
    async def _get_active_bots(self) -> List[Dict[str, Any]]:
        """Получить список активных ботов из main.db"""
        db_url = f"sqlite+aiosqlite:///{self.settings.MAIN_DB_PATH.absolute()}"
        engine = create_async_engine(db_url, echo=False)
        
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        bots = []
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(Bot).where(Bot.is_active == True)
                )
                for bot in result.scalars().all():
                    bots.append({
                        "uuid": bot.uuid,
                        "name": bot.name,
                        "bot_token": bot.bot_token
                    })
        finally:
            await engine.dispose()
        
        return bots
    
    async def _check_bot_subscriptions(self, bot: Dict[str, Any]) -> Dict[str, int]:
        """
        Проверить подписки конкретного бота
        
        Returns:
            {"expired_kicked": int, "expiring_notified": int}
        """
        bot_uuid = bot["uuid"]
        bot_token = bot["bot_token"]
        
        db_path = self.settings.get_bot_db_path(bot_uuid)
        
        if not db_path.exists():
            logger.warning(f"БД бота {bot_uuid} не найдена: {db_path}")
            return {"expired_kicked": 0, "expiring_notified": 0}
        
        db_url = f"sqlite+aiosqlite:///{db_path.absolute()}"
        engine = create_async_engine(db_url, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        result = {"expired_kicked": 0, "expiring_notified": 0}
        
        try:
            async with async_session() as session:
                now = datetime.utcnow()
                notify_threshold = now + timedelta(days=NOTIFY_BEFORE_DAYS)
                
                # 1. Находим истёкшие подписки для кика
                expired_query = (
                    select(Subscription, User, Channel)
                    .join(User, Subscription.user_id == User.id)
                    .join(Channel, Subscription.channel_id == Channel.id)
                    .where(
                        and_(
                            Subscription.is_active == True,
                            Subscription.auto_kicked == False,
                            Subscription.expires_at < now
                        )
                    )
                    .limit(BATCH_SIZE)
                )
                
                expired_result = await session.execute(expired_query)
                expired_subs = expired_result.all()
                
                # 2. Находим подписки для уведомления (истекают в течение 1 дня)
                expiring_query = (
                    select(Subscription, User, Channel)
                    .join(User, Subscription.user_id == User.id)
                    .join(Channel, Subscription.channel_id == Channel.id)
                    .where(
                        and_(
                            Subscription.is_active == True,
                            Subscription.notified_expiring == False,
                            Subscription.expires_at > now,
                            Subscription.expires_at <= notify_threshold
                        )
                    )
                    .limit(BATCH_SIZE)
                )
                
                expiring_result = await session.execute(expiring_query)
                expiring_subs = expiring_result.all()
                
                # Обрабатываем истёкшие подписки
                for sub, user, channel in expired_subs:
                    kicked = await self._kick_user(
                        bot_uuid=bot_uuid,
                        bot_token=bot_token,
                        subscription=sub,
                        user=user,
                        channel=channel
                    )
                    if kicked:
                        # Обновляем статус в БД
                        sub.is_active = False
                        sub.auto_kicked = True
                        result["expired_kicked"] += 1
                
                # Обрабатываем подписки для уведомления
                for sub, user, channel in expiring_subs:
                    notified = await self._notify_expiring(
                        bot_token=bot_token,
                        subscription=sub,
                        user=user,
                        channel=channel
                    )
                    if notified:
                        sub.notified_expiring = True
                        result["expiring_notified"] += 1
                
                await session.commit()
        
        except Exception as e:
            logger.exception(f"Ошибка проверки подписок бота {bot_uuid}: {e}")
        finally:
            await engine.dispose()
        
        return result
    
    async def _kick_user(
        self,
        bot_uuid: str,
        bot_token: str,
        subscription: Subscription,
        user: User,
        channel: Channel
    ) -> bool:
        """
        Удалить пользователя из канала
        
        Returns:
            True если успешно
        """
        logger.info(
            f"Кик пользователя {user.telegram_id} из канала {channel.title} "
            f"(подписка {subscription.id}, бот {bot_uuid})"
        )
        
        # Отправляем запрос в userbot API
        try:
            result = await self._userbot_service.kick_user(
                bot_uuid=bot_uuid,
                user_telegram_id=user.telegram_id,
                channel_id=subscription.channel_id,
                subscription_id=subscription.id,
                sync=True  # Ждём результата
            )
            
            if result.get("success"):
                # Отправляем уведомление пользователю
                await self._send_expiry_notification(
                    bot_token=bot_token,
                    user_telegram_id=user.telegram_id,
                    channel_title=channel.title
                )
                return True
            else:
                logger.error(
                    f"Не удалось кикнуть пользователя {user.telegram_id}: "
                    f"{result.get('error')}"
                )
                return False
        
        except Exception as e:
            logger.exception(f"Ошибка кика пользователя {user.telegram_id}: {e}")
            return False
    
    async def _notify_expiring(
        self,
        bot_token: str,
        subscription: Subscription,
        user: User,
        channel: Channel
    ) -> bool:
        """
        Отправить уведомление об истечении подписки
        
        Returns:
            True если успешно
        """
        expires_at = subscription.expires_at
        time_left = expires_at - datetime.utcnow()
        hours_left = max(1, int(time_left.total_seconds() / 3600))
        
        if hours_left >= 24:
            time_str = f"{hours_left // 24} дн."
        else:
            time_str = f"{hours_left} ч."
        
        message = (
            f"⚠️ <b>Внимание!</b>\n\n"
            f"Ваша подписка на канал <b>{channel.title}</b> "
            f"истекает через <b>{time_str}</b>\n\n"
            f"📅 Дата окончания: {expires_at.strftime('%d.%m.%Y %H:%M')} UTC\n\n"
            f"Продлите подписку, чтобы сохранить доступ к каналу."
        )
        
        success = await self._send_telegram_message(
            bot_token=bot_token,
            chat_id=user.telegram_id,
            text=message
        )
        
        if success:
            logger.info(
                f"Уведомление отправлено пользователю {user.telegram_id} "
                f"о канале {channel.title}"
            )
        
        return success
    
    async def _send_expiry_notification(
        self,
        bot_token: str,
        user_telegram_id: int,
        channel_title: str
    ) -> bool:
        """Отправить уведомление об истечении подписки и кике"""
        message = (
            f"❌ <b>Подписка истекла</b>\n\n"
            f"Ваша подписка на канал <b>{channel_title}</b> истекла.\n"
            f"Вы были удалены из канала.\n\n"
            f"Для возобновления доступа оформите новую подписку."
        )
        
        return await self._send_telegram_message(
            bot_token=bot_token,
            chat_id=user_telegram_id,
            text=message
        )
    
    async def _send_telegram_message(
        self,
        bot_token: str,
        chat_id: int,
        text: str
    ) -> bool:
        """
        Отправить сообщение через Telegram Bot API
        
        Returns:
            True если успешно
        """
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "HTML"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("ok", False)
                else:
                    logger.warning(
                        f"Telegram API error: {response.status_code} - {response.text}"
                    )
                    return False
        
        except httpx.ConnectError:
            logger.warning(f"Не удалось подключиться к Telegram API")
            return False
        except Exception as e:
            logger.exception(f"Ошибка отправки сообщения в Telegram: {e}")
            return False
    
    async def check_now(self) -> Dict[str, Any]:
        """
        Выполнить проверку немедленно (для ручного вызова)
        
        Returns:
            Результаты проверки
        """
        logger.info("Запуск немедленной проверки подписок...")
        
        bots = await self._get_active_bots()
        results = {
            "bots_checked": len(bots),
            "total_expired_kicked": 0,
            "total_expiring_notified": 0,
            "bot_results": []
        }
        
        for bot in bots:
            try:
                result = await self._check_bot_subscriptions(bot)
                results["total_expired_kicked"] += result.get("expired_kicked", 0)
                results["total_expiring_notified"] += result.get("expiring_notified", 0)
                results["bot_results"].append({
                    "uuid": bot["uuid"],
                    "name": bot["name"],
                    **result
                })
            except Exception as e:
                logger.error(f"Ошибка проверки бота {bot['uuid']}: {e}")
                results["bot_results"].append({
                    "uuid": bot["uuid"],
                    "name": bot["name"],
                    "error": str(e)
                })
        
        return results


# Глобальный экземпляр
_subscription_checker: Optional[SubscriptionChecker] = None


def get_subscription_checker() -> SubscriptionChecker:
    """Получить глобальный экземпляр сервиса"""
    global _subscription_checker
    if _subscription_checker is None:
        _subscription_checker = SubscriptionChecker()
    return _subscription_checker


async def start_subscription_checker():
    """Запустить сервис проверки подписок"""
    checker = get_subscription_checker()
    await checker.start()


async def stop_subscription_checker():
    """Остановить сервис проверки подписок"""
    checker = get_subscription_checker()
    await checker.stop()
