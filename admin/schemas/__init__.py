"""Admin schemas package."""

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
from .user import (
    UserUpdate,
    UserBan,
    GrantAccess,
    UserResponse,
    UserDetailResponse,
    UserListResponse,
)
from .subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionListResponse,
    SubscriptionStats,
)
from .payment import (
    PaymentCreate,
    ManualPaymentCreate,
    ManualConfirm,
    PaymentResponse,
    PaymentListResponse,
    PaymentStats,
    RevenueByDay,
)
from .promocode import (
    PromocodeCreate,
    PromocodeUpdate,
    PromocodeResponse,
    PromocodeListResponse,
    PromocodeStats,
)
from .broadcast import (
    BroadcastCreate,
    BroadcastUpdate,
    BroadcastResponse,
    BroadcastListResponse,
    BroadcastStats,
)
from .menu import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemReorder,
    MenuItemResponse,
    MenuItemFlatResponse,
    MenuTreeResponse,
    MenuItemListResponse,
)
from .faq import (
    FAQItemCreate,
    FAQItemUpdate,
    FAQItemResponse,
    FAQItemListResponse,
    FAQStats,
)
from .settings import (
    SettingItem,
    SettingUpdate,
    SettingsBulkUpdate,
    BotSettings,
    MessagesSettings,
    SettingsResponse,
    SettingsListResponse,
)

__all__ = [
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
    # User
    "UserUpdate",
    "UserBan",
    "GrantAccess",
    "UserResponse",
    "UserDetailResponse",
    "UserListResponse",
    # Subscription
    "SubscriptionCreate",
    "SubscriptionUpdate",
    "SubscriptionResponse",
    "SubscriptionListResponse",
    "SubscriptionStats",
    # Payment
    "PaymentCreate",
    "ManualPaymentCreate",
    "ManualConfirm",
    "PaymentResponse",
    "PaymentListResponse",
    "PaymentStats",
    "RevenueByDay",
    # Promocode
    "PromocodeCreate",
    "PromocodeUpdate",
    "PromocodeResponse",
    "PromocodeListResponse",
    "PromocodeStats",
    # Broadcast
    "BroadcastCreate",
    "BroadcastUpdate",
    "BroadcastResponse",
    "BroadcastListResponse",
    "BroadcastStats",
    # Menu
    "MenuItemCreate",
    "MenuItemUpdate",
    "MenuItemReorder",
    "MenuItemResponse",
    "MenuItemFlatResponse",
    "MenuTreeResponse",
    "MenuItemListResponse",
    # FAQ
    "FAQItemCreate",
    "FAQItemUpdate",
    "FAQItemResponse",
    "FAQItemListResponse",
    "FAQStats",
    # Settings
    "SettingItem",
    "SettingUpdate",
    "SettingsBulkUpdate",
    "BotSettings",
    "MessagesSettings",
    "SettingsResponse",
    "SettingsListResponse",
]
