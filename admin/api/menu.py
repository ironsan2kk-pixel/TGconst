"""Menu API endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from admin.database import get_session
from admin.schemas.menu import (
    MenuItemCreate, 
    MenuItemUpdate, 
    MenuItemReorder,
)
from bot.models import MenuItem

router = APIRouter(tags=["Menu"])


# === Response helpers ===

def _build_menu_item_response(item: MenuItem, children: list = None) -> dict:
    """Build response dict for a menu item."""
    return {
        "id": item.id,
        "parent_id": item.parent_id,
        "type": item.type,
        "system_action": item.system_action,
        "text_ru": item.text_ru,
        "text_en": item.text_en,
        "icon": item.icon,
        "value": item.value,
        "photo_file_id": item.photo_file_id,
        "visibility": item.visibility,
        "visibility_language": item.visibility_language,
        "sort_order": item.sort_order,
        "is_active": item.is_active,
        "created_at": item.created_at,
        "children": children or []
    }


async def _build_tree(session: AsyncSession, parent_id: int = None) -> list:
    """Recursively build menu tree."""
    result = await session.execute(
        select(MenuItem)
        .where(MenuItem.parent_id == parent_id)
        .order_by(MenuItem.sort_order)
    )
    items = result.scalars().all()
    
    tree = []
    for item in items:
        children = await _build_tree(session, item.id)
        tree.append(_build_menu_item_response(item, children))
    
    return tree


# === Predefined Templates (MUST be before /{item_id} route!) ===

MENU_TEMPLATES = {
    "crypto_signals": {
        "name": "Крипто-сигналы / Crypto Signals",
        "description_ru": "Шаблон для продажи доступа к крипто-сигналам",
        "description_en": "Template for selling access to crypto signals",
        "items": [
            {
                "type": "system",
                "system_action": "tariffs",
                "text_ru": "Получить доступ",
                "text_en": "Get access",
                "icon": "🚀",
                "sort_order": 1,
                "visibility": "all"
            },
            {
                "type": "system",
                "system_action": "subscriptions",
                "text_ru": "Мои подписки",
                "text_en": "My subscriptions",
                "icon": "💳",
                "sort_order": 2,
                "visibility": "all"
            },
            {
                "type": "section",
                "text_ru": "Настройки",
                "text_en": "Settings",
                "icon": "⚙️",
                "sort_order": 3,
                "visibility": "subscribed",
                "children": []
            },
            {
                "type": "text",
                "text_ru": "Контакты",
                "text_en": "Contacts",
                "icon": "📞",
                "value": "📞 Контакты / Contacts\n\nAdmin: @admin\nSupport: @support\nChannel: @channel",
                "sort_order": 4,
                "visibility": "all"
            },
            {
                "type": "system",
                "system_action": "promocode",
                "text_ru": "Промокод",
                "text_en": "Promocode",
                "icon": "🎁",
                "sort_order": 5,
                "visibility": "all"
            },
        ]
    },
    "channel_access": {
        "name": "Продажа каналов / Channel Access",
        "description_ru": "Базовый шаблон для продажи доступа к каналам",
        "description_en": "Basic template for selling channel access",
        "items": [
            {
                "type": "system",
                "system_action": "tariffs",
                "text_ru": "Тарифы",
                "text_en": "Plans",
                "icon": "📺",
                "sort_order": 1,
                "visibility": "not_subscribed"
            },
            {
                "type": "system",
                "system_action": "subscriptions",
                "text_ru": "Мои подписки",
                "text_en": "My subscriptions",
                "icon": "💳",
                "sort_order": 2,
                "visibility": "all"
            },
            {
                "type": "system",
                "system_action": "promocode",
                "text_ru": "Промокод",
                "text_en": "Promocode",
                "icon": "🎁",
                "sort_order": 3,
                "visibility": "all"
            },
            {
                "type": "system",
                "system_action": "language",
                "text_ru": "Язык",
                "text_en": "Language",
                "icon": "🌐",
                "sort_order": 4,
                "visibility": "all"
            },
            {
                "type": "system",
                "system_action": "support",
                "text_ru": "Поддержка",
                "text_en": "Support",
                "icon": "💬",
                "sort_order": 5,
                "visibility": "all"
            },
        ]
    },
}


@router.get("/templates")
async def get_menu_templates():
    """Get available menu templates."""
    templates = []
    for key, data in MENU_TEMPLATES.items():
        templates.append({
            "id": key,
            "name": data["name"],
            "description_ru": data["description_ru"],
            "description_en": data["description_en"],
            "items_count": len(data["items"])
        })
    return {"items": templates}


@router.post("/templates/{template_id}/apply")
async def apply_menu_template(
    template_id: str,
    clear_existing: bool = True,
    session: AsyncSession = Depends(get_session)
):
    """Apply a menu template."""
    if template_id not in MENU_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = MENU_TEMPLATES[template_id]
    
    # Optionally clear existing menu items
    if clear_existing:
        await session.execute(delete(MenuItem))
        await session.commit()
    
    # Create menu items from template
    created_items = []
    for item_data in template["items"]:
        children = item_data.pop("children", [])
        
        item = MenuItem(
            parent_id=None,
            type=item_data.get("type", "text"),
            system_action=item_data.get("system_action"),
            text_ru=item_data.get("text_ru", ""),
            text_en=item_data.get("text_en"),
            icon=item_data.get("icon"),
            value=item_data.get("value"),
            visibility=item_data.get("visibility", "all"),
            visibility_language=item_data.get("visibility_language", "all"),
            sort_order=item_data.get("sort_order", 0),
            is_active=True
        )
        session.add(item)
        await session.flush()
        created_items.append(item)
        
        # Create children if any
        for child_data in children:
            child = MenuItem(
                parent_id=item.id,
                type=child_data.get("type", "text"),
                system_action=child_data.get("system_action"),
                text_ru=child_data.get("text_ru", ""),
                text_en=child_data.get("text_en"),
                icon=child_data.get("icon"),
                value=child_data.get("value"),
                visibility=child_data.get("visibility", "all"),
                visibility_language=child_data.get("visibility_language", "all"),
                sort_order=child_data.get("sort_order", 0),
                is_active=True
            )
            session.add(child)
    
    await session.commit()
    
    return {
        "success": True,
        "message": f"Template '{template['name']}' applied successfully",
        "items_created": len(created_items)
    }


# === Tree and List routes ===

@router.get("/tree")
async def get_menu_tree(
    session: AsyncSession = Depends(get_session)
):
    """Get full menu tree structure."""
    tree = await _build_tree(session, None)
    return {"items": tree}


@router.get("")
async def get_menu_items(
    parent_id: int = Query(None, description="Filter by parent ID"),
    session: AsyncSession = Depends(get_session)
):
    """Get menu items list."""
    query = select(MenuItem).order_by(MenuItem.sort_order)
    
    if parent_id is not None:
        query = query.where(MenuItem.parent_id == parent_id)
    
    result = await session.execute(query)
    items = result.scalars().all()
    
    return {
        "items": [
            _build_menu_item_response(item, [])
            for item in items
        ],
        "total": len(items)
    }


# === CRUD routes (/{item_id} MUST be AFTER /templates) ===

@router.get("/{item_id}")
async def get_menu_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get menu item by ID with children."""
    result = await session.execute(
        select(MenuItem).where(MenuItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    children = await _build_tree(session, item.id)
    return _build_menu_item_response(item, children)


@router.post("")
async def create_menu_item(
    data: MenuItemCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new menu item."""
    # Validate parent exists if provided
    if data.parent_id is not None:
        parent = await session.get(MenuItem, data.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent menu item not found")
    
    item = MenuItem(
        parent_id=data.parent_id,
        type=data.type,
        system_action=data.system_action,
        text_ru=data.text_ru,
        text_en=data.text_en,
        icon=data.icon,
        value=data.value,
        photo_file_id=data.photo_file_id if hasattr(data, 'photo_file_id') else None,
        visibility=data.visibility,
        visibility_language=data.visibility_language,
        sort_order=data.sort_order,
        is_active=data.is_active
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    return _build_menu_item_response(item, [])


@router.patch("/{item_id}")
async def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a menu item."""
    result = await session.execute(
        select(MenuItem).where(MenuItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await session.commit()
    await session.refresh(item)
    
    children = await _build_tree(session, item.id)
    return _build_menu_item_response(item, children)


@router.delete("/{item_id}")
async def delete_menu_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a menu item and its children."""
    result = await session.execute(
        select(MenuItem).where(MenuItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    await session.delete(item)
    await session.commit()
    
    return {"success": True, "message": "Menu item deleted"}


@router.post("/reorder")
async def reorder_menu_items(
    data: MenuItemReorder,
    session: AsyncSession = Depends(get_session)
):
    """Reorder menu items."""
    for item_data in data.items:
        result = await session.execute(
            select(MenuItem).where(MenuItem.id == item_data["id"])
        )
        item = result.scalar_one_or_none()
        if item:
            item.sort_order = item_data.get("sort_order", 0)
            if "parent_id" in item_data:
                item.parent_id = item_data["parent_id"]
    
    await session.commit()
    return {"success": True, "message": "Menu items reordered"}


@router.post("/{item_id}/duplicate")
async def duplicate_menu_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Duplicate a menu item."""
    result = await session.execute(
        select(MenuItem).where(MenuItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    new_item = MenuItem(
        parent_id=item.parent_id,
        type=item.type,
        system_action=item.system_action,
        text_ru=f"{item.text_ru} (copy)",
        text_en=f"{item.text_en} (copy)" if item.text_en else f"{item.text_ru} (copy)",
        icon=item.icon,
        value=item.value,
        photo_file_id=item.photo_file_id,
        visibility=item.visibility,
        visibility_language=item.visibility_language,
        sort_order=item.sort_order + 1,
        is_active=False
    )
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    
    return _build_menu_item_response(new_item, [])

