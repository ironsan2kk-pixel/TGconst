"""
Callback-обработчики админ-панели.

Основная логика админки находится в bot/handlers/admin.py,
так как там используются и callback и message handlers.
Этот файл оставлен для совместимости и возможного расширения.
"""

from aiogram import Router

router = Router()

# Все callback handlers для админки находятся в bot/handlers/admin.py
# так как они тесно связаны с FSM и message handlers.
