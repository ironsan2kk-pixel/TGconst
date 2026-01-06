"""
Сервисы приложения
"""

from .cryptobot import CryptoBotAPI, CryptoBotError
from .userbot import UserbotService, get_userbot_service
from .subscription_checker import (
    SubscriptionChecker,
    get_subscription_checker,
    start_subscription_checker,
    stop_subscription_checker
)
from .bot_manager import (
    BotManager,
    BotProcess,
    get_bot_manager,
    start_bot_manager,
    stop_bot_manager
)

__all__ = [
    # CryptoBot
    "CryptoBotAPI", 
    "CryptoBotError",
    # Userbot
    "UserbotService",
    "get_userbot_service",
    # Subscription Checker
    "SubscriptionChecker",
    "get_subscription_checker",
    "start_subscription_checker",
    "stop_subscription_checker",
    # Bot Manager (Этап 13)
    "BotManager",
    "BotProcess",
    "get_bot_manager",
    "start_bot_manager",
    "stop_bot_manager"
]
