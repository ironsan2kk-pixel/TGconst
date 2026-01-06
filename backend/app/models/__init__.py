"""
Модели базы данных

main_db.py - модели для главной базы (main.db)
bot_db.py - модели для базы каждого бота (bot.db)
"""
from .main_db import Admin, Bot, UserbotConfig
from .bot_db import (
    Channel, 
    Tariff, 
    User, 
    Subscription, 
    Payment, 
    Promocode, 
    Broadcast
)

__all__ = [
    # Main DB
    "Admin",
    "Bot", 
    "UserbotConfig",
    # Bot DB
    "Channel",
    "Tariff",
    "User",
    "Subscription",
    "Payment",
    "Promocode",
    "Broadcast",
]
