"""
Действия userbot для работы с каналами.
"""

from .invite import (
    invite_to_channels,
    invite_user_to_tariff_channels,
    invite_user_to_subscription_channels,
)

from .kick import (
    kick_from_channels,
    kick_user_from_tariff_channels,
    kick_user_from_subscription_channels,
    kick_user_from_all_channels,
)

__all__ = [
    # Invite
    'invite_to_channels',
    'invite_user_to_tariff_channels',
    'invite_user_to_subscription_channels',
    # Kick
    'kick_from_channels',
    'kick_user_from_tariff_channels',
    'kick_user_from_subscription_channels',
    'kick_user_from_all_channels',
]
