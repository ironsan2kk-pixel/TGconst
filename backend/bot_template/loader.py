"""
Создание экземпляров Bot и Dispatcher для Aiogram 3
"""
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage


def create_bot(token: str) -> Bot:
    """
    Создание экземпляра бота.
    
    Args:
        token: Токен бота от @BotFather
        
    Returns:
        Экземпляр Bot
    """
    return Bot(
        token=token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )


def create_dispatcher() -> Dispatcher:
    """
    Создание диспетчера с хранилищем состояний.
    
    Returns:
        Экземпляр Dispatcher
    """
    # Используем MemoryStorage для FSM
    # В продакшене можно заменить на RedisStorage
    storage = MemoryStorage()
    
    dp = Dispatcher(storage=storage)
    
    return dp
