"""
Диагностика меню - запусти: python test_menu.py
"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    print("=" * 50)
    print("ДИАГНОСТИКА МЕНЮ")
    print("=" * 50)
    
    # 1. Check database
    print("\n1. Проверка БД...")
    try:
        from bot.database import async_session_maker
        from bot.models import MenuItem
        from sqlalchemy import select
        
        async with async_session_maker() as session:
            result = await session.execute(select(MenuItem))
            items = result.scalars().all()
            print(f"   ✓ Пунктов меню в БД: {len(items)}")
            for item in items:
                print(f"      - [{item.id}] {item.type}: {item.text_ru}")
    except Exception as e:
        print(f"   ✗ Ошибка БД: {e}")
    
    # 2. Check handlers
    print("\n2. Проверка хендлеров...")
    try:
        from bot.handlers import setup_handlers
        router = setup_handlers()
        print(f"   ✓ Роутер создан")
        
        # Check for menu:main handler
        from bot.handlers import menu_navigation
        print(f"   ✓ menu_navigation импортирован")
    except Exception as e:
        print(f"   ✗ Ошибка хендлеров: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Check menu_navigation functions
    print("\n3. Проверка функций menu_navigation...")
    try:
        from bot.handlers.menu_navigation import get_menu_items, build_menu_keyboard
        print(f"   ✓ get_menu_items импортирован")
        print(f"   ✓ build_menu_keyboard импортирован")
    except Exception as e:
        print(f"   ✗ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test())
