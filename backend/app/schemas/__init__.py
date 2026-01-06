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
from .promocode import (
    PromocodeCreate,
    PromocodeUpdate,
    PromocodeResponse,
    PromocodeListResponse,
    PromocodeValidateRequest,
    PromocodeValidateResponse,
    PromocodeClearLimitRequest,
)
from .broadcast import (
    BroadcastCreate,
    BroadcastUpdate,
    BroadcastResponse,
    BroadcastListResponse,
    BroadcastStartResponse,
    BroadcastCancelResponse,
    BroadcastStatsResponse,
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
    # Promocode
    "PromocodeCreate",
    "PromocodeUpdate",
    "PromocodeResponse",
    "PromocodeListResponse",
    "PromocodeValidateRequest",
    "PromocodeValidateResponse",
    "PromocodeClearLimitRequest",
    # Broadcast
    "BroadcastCreate",
    "BroadcastUpdate",
    "BroadcastResponse",
    "BroadcastListResponse",
    "BroadcastStartResponse",
    "BroadcastCancelResponse",
    "BroadcastStatsResponse",
]
