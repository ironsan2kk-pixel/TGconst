"""
Менеджер (оркестратор) ботов.

Отвечает за:
- Запуск ботов как subprocess
- Остановку ботов по PID
- Отслеживание статуса процессов
- Автозапуск активных ботов при старте backend
"""
import os
import sys
import signal
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings, PROJECT_ROOT
from ..database import get_main_session
from ..models.main_db import Bot

logger = logging.getLogger(__name__)


@dataclass
class BotProcess:
    """Информация о запущенном процессе бота"""
    uuid: str
    pid: int
    process: asyncio.subprocess.Process
    started_at: datetime = field(default_factory=datetime.utcnow)


class BotManager:
    """
    Менеджер процессов ботов.
    
    Singleton-класс для управления всеми процессами ботов.
    """
    
    _instance: Optional["BotManager"] = None
    
    def __new__(cls) -> "BotManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._processes: Dict[str, BotProcess] = {}
        self._settings = get_settings()
        self._lock = asyncio.Lock()
        
        # Путь к Python интерпретатору
        self._python_path = sys.executable
        
        # Путь к run.py шаблона бота
        self._bot_runner_path = PROJECT_ROOT / "backend" / "bot_template" / "run.py"
        
        logger.info("BotManager инициализирован")
    
    @property
    def running_bots(self) -> Dict[str, BotProcess]:
        """Словарь запущенных ботов"""
        return self._processes.copy()
    
    def is_running(self, bot_uuid: str) -> bool:
        """Проверить, запущен ли бот"""
        if bot_uuid not in self._processes:
            return False
        
        process = self._processes[bot_uuid].process
        return process.returncode is None
    
    def get_pid(self, bot_uuid: str) -> Optional[int]:
        """Получить PID процесса бота"""
        if bot_uuid in self._processes:
            return self._processes[bot_uuid].pid
        return None
    
    async def start_bot(self, bot_uuid: str, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Запустить бота.
        
        Args:
            bot_uuid: UUID бота
            db: Сессия БД (опционально, создастся автоматически)
        
        Returns:
            Dict с информацией о результате
        """
        async with self._lock:
            # Проверяем, не запущен ли уже
            if self.is_running(bot_uuid):
                return {
                    "success": True,
                    "already_running": True,
                    "pid": self._processes[bot_uuid].pid,
                    "message": "Бот уже запущен"
                }
            
            # Проверяем существование бота в БД
            should_close_db = db is None
            if db is None:
                db = await get_main_session()
            
            try:
                result = await db.execute(
                    select(Bot).where(Bot.uuid == bot_uuid)
                )
                bot = result.scalar_one_or_none()
                
                if bot is None:
                    return {
                        "success": False,
                        "message": f"Бот {bot_uuid} не найден в базе данных"
                    }
                
                # Проверяем существование папки бота
                bot_dir = self._settings.get_bot_dir(bot_uuid)
                if not bot_dir.exists():
                    return {
                        "success": False,
                        "message": f"Папка бота не существует: {bot_dir}"
                    }
                
                # Проверяем существование bot.db
                bot_db_path = self._settings.get_bot_db_path(bot_uuid)
                if not bot_db_path.exists():
                    return {
                        "success": False,
                        "message": f"База данных бота не существует: {bot_db_path}"
                    }
                
                # Запускаем процесс
                try:
                    process = await asyncio.create_subprocess_exec(
                        self._python_path,
                        str(self._bot_runner_path),
                        f"--bot-uuid={bot_uuid}",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=str(PROJECT_ROOT),
                        # Устанавливаем переменные окружения
                        env={
                            **os.environ,
                            "PYTHONPATH": str(PROJECT_ROOT),
                            "BOT_UUID": bot_uuid
                        }
                    )
                    
                    pid = process.pid
                    
                    # Ждём немного чтобы убедиться что процесс не упал сразу
                    await asyncio.sleep(0.5)
                    
                    if process.returncode is not None:
                        # Процесс уже завершился — ошибка
                        stdout, stderr = await process.communicate()
                        error_msg = stderr.decode() if stderr else stdout.decode()
                        logger.error(f"Бот {bot_uuid} упал при запуске: {error_msg}")
                        return {
                            "success": False,
                            "message": f"Бот упал при запуске: {error_msg[:500]}"
                        }
                    
                    # Сохраняем информацию о процессе
                    self._processes[bot_uuid] = BotProcess(
                        uuid=bot_uuid,
                        pid=pid,
                        process=process
                    )
                    
                    # Обновляем БД
                    bot.is_active = True
                    bot.process_pid = pid
                    await db.commit()
                    
                    # Запускаем фоновый мониторинг процесса
                    asyncio.create_task(self._monitor_process(bot_uuid))
                    
                    logger.info(f"Бот {bot_uuid} запущен с PID {pid}")
                    
                    return {
                        "success": True,
                        "pid": pid,
                        "message": f"Бот успешно запущен (PID: {pid})"
                    }
                    
                except Exception as e:
                    logger.exception(f"Ошибка запуска бота {bot_uuid}")
                    return {
                        "success": False,
                        "message": f"Ошибка запуска процесса: {str(e)}"
                    }
                    
            finally:
                if should_close_db:
                    await db.close()
    
    async def stop_bot(self, bot_uuid: str, db: Optional[AsyncSession] = None, force: bool = False) -> Dict[str, Any]:
        """
        Остановить бота.
        
        Args:
            bot_uuid: UUID бота
            db: Сессия БД (опционально)
            force: Принудительное завершение (SIGKILL)
        
        Returns:
            Dict с информацией о результате
        """
        async with self._lock:
            should_close_db = db is None
            if db is None:
                db = await get_main_session()
            
            try:
                # Проверяем есть ли процесс в памяти
                if bot_uuid not in self._processes:
                    # Пробуем по PID из БД
                    result = await db.execute(
                        select(Bot).where(Bot.uuid == bot_uuid)
                    )
                    bot = result.scalar_one_or_none()
                    
                    if bot is None:
                        return {
                            "success": False,
                            "message": "Бот не найден"
                        }
                    
                    if not bot.is_active:
                        return {
                            "success": True,
                            "already_stopped": True,
                            "message": "Бот уже остановлен"
                        }
                    
                    # Пробуем убить по сохранённому PID
                    if bot.process_pid:
                        try:
                            os.kill(bot.process_pid, signal.SIGTERM if not force else signal.SIGKILL)
                            await asyncio.sleep(0.5)
                        except ProcessLookupError:
                            pass  # Процесс уже не существует
                        except Exception as e:
                            logger.warning(f"Ошибка при остановке процесса {bot.process_pid}: {e}")
                    
                    # Обновляем БД
                    bot.is_active = False
                    bot.process_pid = None
                    await db.commit()
                    
                    return {
                        "success": True,
                        "message": "Бот остановлен"
                    }
                
                # Есть процесс в памяти
                bot_process = self._processes[bot_uuid]
                process = bot_process.process
                pid = bot_process.pid
                
                if process.returncode is None:
                    # Процесс ещё работает
                    try:
                        if force:
                            process.kill()
                        else:
                            process.terminate()
                        
                        # Ждём завершения (максимум 10 секунд)
                        try:
                            await asyncio.wait_for(process.wait(), timeout=10.0)
                        except asyncio.TimeoutError:
                            # Принудительно убиваем
                            process.kill()
                            await process.wait()
                        
                    except Exception as e:
                        logger.warning(f"Ошибка при остановке процесса {pid}: {e}")
                
                # Удаляем из словаря
                del self._processes[bot_uuid]
                
                # Обновляем БД
                result = await db.execute(
                    select(Bot).where(Bot.uuid == bot_uuid)
                )
                bot = result.scalar_one_or_none()
                if bot:
                    bot.is_active = False
                    bot.process_pid = None
                    await db.commit()
                
                logger.info(f"Бот {bot_uuid} остановлен (был PID {pid})")
                
                return {
                    "success": True,
                    "pid": pid,
                    "message": f"Бот остановлен (был PID: {pid})"
                }
                
            finally:
                if should_close_db:
                    await db.close()
    
    async def restart_bot(self, bot_uuid: str, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Перезапустить бота.
        
        Args:
            bot_uuid: UUID бота
            db: Сессия БД (опционально)
        
        Returns:
            Dict с информацией о результате
        """
        # Останавливаем
        stop_result = await self.stop_bot(bot_uuid, db)
        if not stop_result["success"] and not stop_result.get("already_stopped"):
            return {
                "success": False,
                "message": f"Ошибка остановки: {stop_result['message']}"
            }
        
        # Небольшая пауза
        await asyncio.sleep(1)
        
        # Запускаем
        start_result = await self.start_bot(bot_uuid, db)
        
        if start_result["success"]:
            return {
                "success": True,
                "pid": start_result.get("pid"),
                "message": "Бот успешно перезапущен"
            }
        else:
            return {
                "success": False,
                "message": f"Ошибка запуска: {start_result['message']}"
            }
    
    async def get_status(self, bot_uuid: str) -> Dict[str, Any]:
        """
        Получить статус бота.
        
        Args:
            bot_uuid: UUID бота
        
        Returns:
            Dict с информацией о статусе
        """
        is_running = self.is_running(bot_uuid)
        pid = self.get_pid(bot_uuid)
        
        started_at = None
        uptime_seconds = None
        
        if bot_uuid in self._processes:
            started_at = self._processes[bot_uuid].started_at
            uptime_seconds = (datetime.utcnow() - started_at).total_seconds()
        
        return {
            "is_running": is_running,
            "pid": pid,
            "started_at": started_at.isoformat() if started_at else None,
            "uptime_seconds": int(uptime_seconds) if uptime_seconds else None
        }
    
    async def _monitor_process(self, bot_uuid: str):
        """
        Фоновый мониторинг процесса бота.
        
        Отслеживает неожиданное завершение процесса и обновляет БД.
        """
        if bot_uuid not in self._processes:
            return
        
        process = self._processes[bot_uuid].process
        
        try:
            # Ждём завершения процесса
            await process.wait()
            
            logger.warning(f"Бот {bot_uuid} неожиданно завершился с кодом {process.returncode}")
            
            # Обновляем БД
            async with self._lock:
                if bot_uuid in self._processes:
                    del self._processes[bot_uuid]
                
                db = await get_main_session()
                try:
                    result = await db.execute(
                        select(Bot).where(Bot.uuid == bot_uuid)
                    )
                    bot = result.scalar_one_or_none()
                    if bot:
                        bot.is_active = False
                        bot.process_pid = None
                        await db.commit()
                finally:
                    await db.close()
                    
        except Exception as e:
            logger.exception(f"Ошибка мониторинга бота {bot_uuid}: {e}")
    
    async def autostart_active_bots(self):
        """
        Автозапуск всех активных ботов.
        
        Вызывается при старте backend для восстановления состояния.
        """
        logger.info("Автозапуск активных ботов...")
        
        db = await get_main_session()
        try:
            # Сначала сбрасываем все PID (процессы могли умереть)
            await db.execute(
                update(Bot).values(process_pid=None)
            )
            await db.commit()
            
            # Получаем список активных ботов
            result = await db.execute(
                select(Bot).where(Bot.is_active == True)
            )
            active_bots = result.scalars().all()
            
            if not active_bots:
                logger.info("Нет активных ботов для автозапуска")
                return
            
            logger.info(f"Найдено {len(active_bots)} активных ботов для запуска")
            
            # Запускаем каждого бота
            for bot in active_bots:
                try:
                    result = await self.start_bot(bot.uuid, db)
                    if result["success"]:
                        logger.info(f"✅ Бот {bot.name} ({bot.uuid}) запущен")
                    else:
                        logger.error(f"❌ Бот {bot.name} ({bot.uuid}) не запущен: {result['message']}")
                        # Помечаем как неактивный
                        bot.is_active = False
                        await db.commit()
                except Exception as e:
                    logger.exception(f"Ошибка запуска бота {bot.uuid}: {e}")
                    bot.is_active = False
                    await db.commit()
                
                # Пауза между запусками чтобы не перегружать
                await asyncio.sleep(0.5)
            
            logger.info("Автозапуск завершён")
            
        finally:
            await db.close()
    
    async def stop_all_bots(self):
        """
        Остановить все запущенные боты.
        
        Вызывается при остановке backend.
        """
        logger.info("Остановка всех ботов...")
        
        uuids = list(self._processes.keys())
        for bot_uuid in uuids:
            try:
                await self.stop_bot(bot_uuid)
            except Exception as e:
                logger.exception(f"Ошибка остановки бота {bot_uuid}: {e}")
        
        logger.info("Все боты остановлены")
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Получить статус всех запущенных ботов.
        
        Returns:
            Dict[uuid] = status info
        """
        result = {}
        for uuid, bot_process in self._processes.items():
            is_running = bot_process.process.returncode is None
            uptime = (datetime.utcnow() - bot_process.started_at).total_seconds()
            
            result[uuid] = {
                "is_running": is_running,
                "pid": bot_process.pid,
                "started_at": bot_process.started_at.isoformat(),
                "uptime_seconds": int(uptime)
            }
        
        return result


# Глобальный экземпляр
_bot_manager: Optional[BotManager] = None


def get_bot_manager() -> BotManager:
    """Получить экземпляр BotManager"""
    global _bot_manager
    if _bot_manager is None:
        _bot_manager = BotManager()
    return _bot_manager


async def start_bot_manager():
    """Запустить менеджер ботов (автозапуск активных)"""
    manager = get_bot_manager()
    await manager.autostart_active_bots()


async def stop_bot_manager():
    """Остановить менеджер ботов"""
    manager = get_bot_manager()
    await manager.stop_all_bots()
