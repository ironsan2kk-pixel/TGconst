"""Settings API endpoints."""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from admin.schemas.settings import (
    SettingItem,
    SettingUpdate,
    SettingsBulkUpdate,
    BotSettings,
    MessagesSettings,
    SettingsResponse,
    SettingsListResponse,
)
from bot.models import Settings

router = APIRouter()


# Default settings keys
DEFAULT_SETTINGS = {
    "bot_token": "",
    "cryptobot_token": "",
    "admin_ids": "[]",
    "default_language": "ru",
    "notify_new_users": "true",
    "notify_payments": "true",
    "welcome_message_ru": "Добро пожаловать! Выберите действие:",
    "welcome_message_en": "Welcome! Choose an action:",
    "support_url": "",
}


async def get_setting(session: AsyncSession, key: str) -> str | None:
    """Get setting value by key."""
    result = await session.execute(
        select(Settings).where(Settings.key == key)
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else DEFAULT_SETTINGS.get(key)


async def set_setting(session: AsyncSession, key: str, value: str | None) -> Settings:
    """Set setting value."""
    result = await session.execute(
        select(Settings).where(Settings.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = value
    else:
        setting = Settings(key=key, value=value)
        session.add(setting)
    
    await session.flush()
    return setting


@router.get("", response_model=SettingsListResponse)
async def get_all_settings(session: AsyncSession = Depends(get_session)):
    """Get all settings."""
    result = await session.execute(select(Settings))
    settings = result.scalars().all()
    
    # Add defaults for missing settings
    existing_keys = {s.key for s in settings}
    items = [
        SettingItem(key=s.key, value=s.value, updated_at=s.updated_at)
        for s in settings
    ]
    
    return SettingsListResponse(
        items=items,
        total=len(items)
    )


@router.get("/grouped", response_model=SettingsResponse)
async def get_grouped_settings(session: AsyncSession = Depends(get_session)):
    """Get settings grouped by category."""
    # Bot settings
    admin_ids_str = await get_setting(session, "admin_ids")
    try:
        admin_ids = json.loads(admin_ids_str) if admin_ids_str else []
    except json.JSONDecodeError:
        admin_ids = []
    
    notify_new_users_str = await get_setting(session, "notify_new_users")
    notify_payments_str = await get_setting(session, "notify_payments")
    
    bot = BotSettings(
        bot_token=await get_setting(session, "bot_token"),
        cryptobot_token=await get_setting(session, "cryptobot_token"),
        admin_ids=admin_ids,
        default_language=await get_setting(session, "default_language") or "ru",
        notify_new_users=notify_new_users_str == "true" if notify_new_users_str else True,
        notify_payments=notify_payments_str == "true" if notify_payments_str else True,
    )
    
    # Message settings
    messages = MessagesSettings(
        welcome_message_ru=await get_setting(session, "welcome_message_ru"),
        welcome_message_en=await get_setting(session, "welcome_message_en"),
        support_url=await get_setting(session, "support_url"),
    )
    
    return SettingsResponse(bot=bot, messages=messages)


@router.get("/{key}")
async def get_setting_value(
    key: str,
    session: AsyncSession = Depends(get_session)
):
    """Get single setting by key."""
    value = await get_setting(session, key)
    return {"key": key, "value": value}


@router.put("/{key}")
async def update_setting(
    key: str,
    data: SettingUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update single setting."""
    setting = await set_setting(session, key, data.value)
    await session.commit()
    await session.refresh(setting)
    
    return {
        "key": setting.key,
        "value": setting.value,
        "updated_at": setting.updated_at.isoformat()
    }


@router.post("/bulk")
async def bulk_update_settings(
    data: SettingsBulkUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update multiple settings at once."""
    updated = []
    
    for key, value in data.settings.items():
        setting = await set_setting(session, key, value)
        updated.append(key)
    
    await session.commit()
    
    return {
        "status": "ok",
        "updated": updated
    }


@router.delete("/{key}")
async def delete_setting(
    key: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a setting (reset to default)."""
    result = await session.execute(
        select(Settings).where(Settings.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if setting:
        await session.delete(setting)
        await session.commit()
    
    return {"status": "ok", "message": f"Setting '{key}' deleted"}
