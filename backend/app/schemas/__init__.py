"""
Pydantic схемы для валидации данных
"""
from .auth import (
    LoginRequest,
    TokenResponse,
    AdminResponse,
)
from .bot import (
    BotCreate,
    BotUpdate,
    BotResponse,
    BotListResponse,
    BotStatusResponse,
)
from .channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelListResponse,
)
from .tariff import (
    TariffCreate,
    TariffUpdate,
    TariffResponse,
    TariffListResponse,
)

__all__ = [
    # Auth
    "LoginRequest",
    "TokenResponse",
    "AdminResponse",
    # Bot
    "BotCreate",
    "BotUpdate",
    "BotResponse",
    "BotListResponse",
    "BotStatusResponse",
    # Channel
    "ChannelCreate",
    "ChannelUpdate",
    "ChannelResponse",
    "ChannelListResponse",
    # Tariff
    "TariffCreate",
    "TariffUpdate",
    "TariffResponse",
    "TariffListResponse",
]
