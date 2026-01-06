"""
Фоновый воркер для выполнения рассылок.

Этот модуль используется шаблоном бота (bot_template) для отправки
сообщений пользователям. В админке (backend API) мы только управляем
статусом рассылки, а реальная отправка происходит в контексте бота.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable, Awaitable, List
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.bot_db import Broadcast, User
from ..api.broadcasts import is_broadcast_cancelled, remove_active_broadcast

logger = logging.getLogger(__name__)


@dataclass
class BroadcastResult:
    """Результат отправки одного сообщения"""
    user_id: int
    telegram_id: int
    success: bool
    error: Optional[str] = None


class BroadcastWorker:
    """
    Воркер для выполнения рассылок.
    
    Используется в контексте бота для отправки сообщений.
    
    Пример использования в боте:
    ```python
    from backend.app.services import BroadcastWorker
    
    async def send_message(user_id: int, text: str, photo: str = None) -> bool:
        # Реализация отправки через aiogram
        try:
            if photo:
                await bot.send_photo(user_id, photo, caption=text)
            else:
                await bot.send_message(user_id, text)
            return True
        except Exception:
            return False
    
    worker = BroadcastWorker(db_session)
    await worker.execute(broadcast_id, send_message)
    ```
    """
    
    def __init__(
        self, 
        db: AsyncSession,
        batch_size: int = 25,
        delay_between_messages: float = 0.05,
        delay_between_batches: float = 1.0
    ):
        """
        Инициализация воркера.
        
        Args:
            db: Сессия базы данных бота
            batch_size: Размер пачки сообщений перед паузой
            delay_between_messages: Задержка между сообщениями (секунды)
            delay_between_batches: Задержка между пачками (секунды)
        """
        self.db = db
        self.batch_size = batch_size
        self.delay_between_messages = delay_between_messages
        self.delay_between_batches = delay_between_batches
    
    async def get_broadcast(self, broadcast_id: int) -> Optional[Broadcast]:
        """Получить рассылку по ID"""
        result = await self.db.execute(
            select(Broadcast).where(Broadcast.id == broadcast_id)
        )
        return result.scalar_one_or_none()
    
    async def get_users_for_broadcast(self) -> List[User]:
        """Получить список пользователей для рассылки"""
        result = await self.db.execute(
            select(User).where(User.is_blocked == False).order_by(User.id)
        )
        return list(result.scalars().all())
    
    async def update_broadcast_progress(
        self, 
        broadcast: Broadcast, 
        sent: int, 
        failed: int
    ) -> None:
        """Обновить прогресс рассылки в БД"""
        broadcast.sent_count = sent
        broadcast.failed_count = failed
        await self.db.commit()
    
    async def complete_broadcast(
        self, 
        broadcast: Broadcast, 
        final_status: str = "completed"
    ) -> None:
        """Завершить рассылку"""
        broadcast.status = final_status
        broadcast.completed_at = datetime.utcnow()
        await self.db.commit()
        
        # Удаляем из активных
        remove_active_broadcast(broadcast.id)
        
        logger.info(
            f"Broadcast {broadcast.id} {final_status}: "
            f"sent={broadcast.sent_count}, failed={broadcast.failed_count}"
        )
    
    async def execute(
        self,
        broadcast_id: int,
        send_func: Callable[[int, str, Optional[str]], Awaitable[bool]],
        on_progress: Optional[Callable[[int, int, int], Awaitable[None]]] = None
    ) -> bool:
        """
        Выполнить рассылку.
        
        Args:
            broadcast_id: ID рассылки
            send_func: Функция отправки сообщения (telegram_id, text, photo) -> success
            on_progress: Callback при обновлении прогресса (sent, failed, total)
        
        Returns:
            True если рассылка завершена успешно, False если отменена
        """
        # Получаем рассылку
        broadcast = await self.get_broadcast(broadcast_id)
        if not broadcast:
            logger.error(f"Broadcast {broadcast_id} not found")
            return False
        
        if broadcast.status != "running":
            logger.warning(f"Broadcast {broadcast_id} is not running: {broadcast.status}")
            return False
        
        # Получаем пользователей
        users = await self.get_users_for_broadcast()
        total_users = len(users)
        
        if total_users == 0:
            logger.warning(f"No users for broadcast {broadcast_id}")
            await self.complete_broadcast(broadcast, "completed")
            return True
        
        # Обновляем total_users (мог измениться с момента создания)
        broadcast.total_users = total_users
        await self.db.commit()
        
        logger.info(f"Starting broadcast {broadcast_id} to {total_users} users")
        
        sent_count = 0
        failed_count = 0
        batch_count = 0
        
        for i, user in enumerate(users):
            # Проверяем отмену
            if is_broadcast_cancelled(broadcast_id):
                logger.info(f"Broadcast {broadcast_id} was cancelled")
                await self.complete_broadcast(broadcast, "cancelled")
                return False
            
            # Отправляем сообщение
            try:
                success = await send_func(
                    user.telegram_id,
                    broadcast.message_text,
                    broadcast.message_photo
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending to {user.telegram_id}: {e}")
                failed_count += 1
            
            batch_count += 1
            
            # Задержка между сообщениями
            if self.delay_between_messages > 0:
                await asyncio.sleep(self.delay_between_messages)
            
            # Пауза после пачки + обновление прогресса
            if batch_count >= self.batch_size:
                batch_count = 0
                
                # Обновляем прогресс в БД
                await self.update_broadcast_progress(broadcast, sent_count, failed_count)
                
                # Callback
                if on_progress:
                    await on_progress(sent_count, failed_count, total_users)
                
                # Пауза между пачками
                if self.delay_between_batches > 0:
                    await asyncio.sleep(self.delay_between_batches)
        
        # Финальное обновление
        await self.update_broadcast_progress(broadcast, sent_count, failed_count)
        await self.complete_broadcast(broadcast, "completed")
        
        if on_progress:
            await on_progress(sent_count, failed_count, total_users)
        
        logger.info(
            f"Broadcast {broadcast_id} completed: "
            f"sent={sent_count}/{total_users}, failed={failed_count}"
        )
        
        return True


async def run_broadcast_worker(
    db: AsyncSession,
    broadcast_id: int,
    send_func: Callable[[int, str, Optional[str]], Awaitable[bool]]
) -> bool:
    """
    Запуск воркера рассылки.
    
    Удобная функция для быстрого запуска.
    
    Args:
        db: Сессия БД бота
        broadcast_id: ID рассылки
        send_func: Функция отправки (telegram_id, text, photo) -> success
    
    Returns:
        True если успешно, False если отменена или ошибка
    """
    worker = BroadcastWorker(db)
    return await worker.execute(broadcast_id, send_func)
