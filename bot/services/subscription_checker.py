"""
Сервис проверки подписок.

Периодически проверяет истекающие и истекшие подписки:
- Уведомляет за 3 дня до окончания
- Уведомляет за 1 день до окончания  
- Автоматически кикает при истечении
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload

from bot.models import Subscription, User, Tariff, TariffChannel, Channel

logger = logging.getLogger(__name__)


class SubscriptionChecker:
    """Периодическая проверка подписок."""
    
    def __init__(
        self,
        check_interval: int = 300,  # 5 минут
        database_url: Optional[str] = None,
    ):
        """
        Инициализация checker'а.
        
        Args:
            check_interval: Интервал проверки в секундах
            database_url: URL базы данных (если не указан, берётся из конфига)
        """
        self.check_interval = check_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # Настраиваем подключение к БД
        if database_url is None:
            from bot.config import config
            database_url = f"sqlite+aiosqlite:///{config.DATABASE_PATH}"
        
        self._engine = create_async_engine(database_url, echo=False)
        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        # Bot для отправки уведомлений
        self._bot = None
    
    async def _get_bot(self):
        """Получить экземпляр бота для отправки сообщений."""
        if self._bot is None:
            from aiogram import Bot
            from bot.config import config
            self._bot = Bot(token=config.BOT_TOKEN)
        return self._bot
    
    async def start(self) -> None:
        """Запустить checker."""
        if self._running:
            logger.warning("Checker is already running")
            return
        
        self._running = True
        logger.info("Subscription checker started")
    
    async def stop(self) -> None:
        """Остановить checker."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Закрываем сессию бота
        if self._bot:
            await self._bot.session.close()
            self._bot = None
        
        logger.info("Subscription checker stopped")
    
    async def run_forever(self) -> None:
        """Запустить бесконечный цикл проверки."""
        await self.start()
        
        while self._running:
            try:
                await self.check_subscriptions()
            except Exception as e:
                logger.error(f"Error in subscription check: {e}", exc_info=True)
            
            # Ждём до следующей проверки
            await asyncio.sleep(self.check_interval)
    
    async def check_subscriptions(self) -> None:
        """Выполнить проверку всех подписок."""
        logger.info("Running subscription check...")
        
        async with self._session_maker() as session:
            # 1. Уведомления за 3 дня
            await self._notify_expiring_soon(session, days=3)
            
            # 2. Уведомления за 1 день
            await self._notify_expiring_soon(session, days=1)
            
            # 3. Обработка истекших подписок
            await self._handle_expired_subscriptions(session)
        
        logger.info("Subscription check completed")
    
    async def _notify_expiring_soon(
        self,
        session: AsyncSession,
        days: int,
    ) -> None:
        """
        Отправить уведомления об истекающих подписках.
        
        Args:
            session: Сессия БД
            days: За сколько дней до истечения уведомлять
        """
        now = datetime.utcnow()
        target_date = now + timedelta(days=days)
        
        # Поле для проверки "уже уведомлён"
        notified_field = 'notified_3days' if days == 3 else 'notified_1day'
        
        # Находим подписки, истекающие в указанный период
        stmt = select(Subscription).where(
            and_(
                Subscription.is_active == True,
                Subscription.expires_at != None,
                Subscription.expires_at <= target_date,
                Subscription.expires_at > now,
                getattr(Subscription, notified_field) == False,
            )
        ).options(
            selectinload(Subscription.user),
            selectinload(Subscription.tariff),
        )
        
        result = await session.execute(stmt)
        subscriptions = result.scalars().all()
        
        if not subscriptions:
            return
        
        logger.info(f"Found {len(subscriptions)} subscriptions expiring in {days} days")
        
        bot = await self._get_bot()
        
        for sub in subscriptions:
            try:
                await self._send_expiration_notice(
                    bot=bot,
                    subscription=sub,
                    days_left=days,
                )
                
                # Отмечаем как уведомлённого
                setattr(sub, notified_field, True)
                
            except Exception as e:
                logger.error(f"Error notifying user {sub.user.telegram_id}: {e}")
        
        await session.commit()
    
    async def _send_expiration_notice(
        self,
        bot,
        subscription: Subscription,
        days_left: int,
    ) -> None:
        """
        Отправить уведомление о скором истечении подписки.
        
        Args:
            bot: Экземпляр бота
            subscription: Подписка
            days_left: Дней до истечения
        """
        from bot.locales import get_text
        from bot.keyboards.inline import renew_subscription_keyboard
        
        user = subscription.user
        tariff = subscription.tariff
        lang = user.language or 'ru'
        
        # Формируем сообщение
        if days_left == 3:
            text = get_text('subscription_expires_3days', lang).format(
                tariff_name=tariff.name_ru if lang == 'ru' else tariff.name_en,
                expires_at=subscription.expires_at.strftime('%d.%m.%Y %H:%M'),
            )
        else:
            text = get_text('subscription_expires_1day', lang).format(
                tariff_name=tariff.name_ru if lang == 'ru' else tariff.name_en,
                expires_at=subscription.expires_at.strftime('%d.%m.%Y %H:%M'),
            )
        
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=text,
                reply_markup=renew_subscription_keyboard(tariff.id, lang),
            )
            logger.info(f"Sent {days_left}-day notice to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send notice to {user.telegram_id}: {e}")
    
    async def _handle_expired_subscriptions(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Обработать истекшие подписки.
        
        - Деактивировать подписку
        - Кикнуть из каналов
        - Уведомить пользователя
        """
        now = datetime.utcnow()
        
        # Находим истекшие активные подписки
        stmt = select(Subscription).where(
            and_(
                Subscription.is_active == True,
                Subscription.expires_at != None,
                Subscription.expires_at <= now,
                Subscription.auto_kicked == False,
            )
        ).options(
            selectinload(Subscription.user),
            selectinload(Subscription.tariff).selectinload(
                Tariff.tariff_channels
            ).selectinload(TariffChannel.channel),
        )
        
        result = await session.execute(stmt)
        subscriptions = result.scalars().all()
        
        if not subscriptions:
            return
        
        logger.info(f"Found {len(subscriptions)} expired subscriptions to process")
        
        from userbot.actions.kick import kick_from_channels
        
        bot = await self._get_bot()
        
        for sub in subscriptions:
            try:
                # Собираем каналы для кика
                channels = [tc.channel for tc in sub.tariff.tariff_channels if tc.channel.is_active]
                
                if channels:
                    # Кикаем из каналов
                    results = await kick_from_channels(
                        user_telegram_id=sub.user.telegram_id,
                        channels=channels,
                    )
                    
                    # Логируем результаты
                    success_count = sum(1 for s, _ in results.values() if s)
                    logger.info(
                        f"Kicked user {sub.user.telegram_id} from {success_count}/{len(channels)} channels"
                    )
                
                # Деактивируем подписку
                sub.is_active = False
                sub.auto_kicked = True
                
                # Уведомляем пользователя
                await self._send_expired_notice(bot, sub)
                
            except Exception as e:
                logger.error(
                    f"Error processing expired subscription {sub.id}: {e}",
                    exc_info=True,
                )
        
        await session.commit()
    
    async def _send_expired_notice(
        self,
        bot,
        subscription: Subscription,
    ) -> None:
        """
        Отправить уведомление об истечении подписки.
        
        Args:
            bot: Экземпляр бота
            subscription: Подписка
        """
        from bot.locales import get_text
        from bot.keyboards.inline import renew_subscription_keyboard
        
        user = subscription.user
        tariff = subscription.tariff
        lang = user.language or 'ru'
        
        text = get_text('subscription_expired', lang).format(
            tariff_name=tariff.name_ru if lang == 'ru' else tariff.name_en,
        )
        
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=text,
                reply_markup=renew_subscription_keyboard(tariff.id, lang),
            )
            logger.info(f"Sent expiration notice to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send expiration notice to {user.telegram_id}: {e}")


async def run_single_check() -> None:
    """Выполнить одну проверку (для ручного запуска)."""
    checker = SubscriptionChecker()
    await checker.check_subscriptions()
    await checker.stop()
