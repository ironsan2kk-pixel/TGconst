"""
Callback handlers для бота
"""

from aiogram import Router

from . import payment

router = Router()
router.include_router(payment.router)

__all__ = ["router"]
