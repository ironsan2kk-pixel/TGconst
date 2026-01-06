#!/usr/bin/env python3
"""
Скрипт для генерации Pyrogram session_string

Запуск:
    python scripts/generate_session.py

После запуска:
1. Введите номер телефона (с кодом страны, например +79001234567)
2. Введите код подтверждения из Telegram
3. Если включена 2FA - введите пароль
4. Скопируйте полученную session_string в .env файл

ВАЖНО: 
- Session string даёт полный доступ к аккаунту!
- Храните его в безопасности
- Не делитесь им ни с кем
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем корень проекта в путь
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pyrogram import Client


async def main():
    print("=" * 60)
    print("Генерация Pyrogram Session String")
    print("=" * 60)
    print()
    
    # Запрашиваем API ID
    api_id = input("Введите USERBOT_API_ID (из my.telegram.org): ").strip()
    if not api_id.isdigit():
        print("Ошибка: API ID должен быть числом")
        return
    
    api_id = int(api_id)
    
    # Запрашиваем API Hash
    api_hash = input("Введите USERBOT_API_HASH: ").strip()
    if not api_hash:
        print("Ошибка: API Hash не может быть пустым")
        return
    
    print()
    print("Создаём клиент Pyrogram...")
    print("Вам нужно будет ввести номер телефона и код подтверждения")
    print()
    
    # Создаём временный клиент для получения session_string
    async with Client(
        name="session_generator",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True
    ) as client:
        # Получаем session_string
        session_string = await client.export_session_string()
        
        me = await client.get_me()
        
        print()
        print("=" * 60)
        print("✅ Успешно!")
        print("=" * 60)
        print()
        print(f"Аккаунт: {me.first_name} (@{me.username})")
        print(f"Telegram ID: {me.id}")
        print()
        print("Ваш USERBOT_SESSION_STRING:")
        print("-" * 60)
        print(session_string)
        print("-" * 60)
        print()
        print("Добавьте эту строку в .env файл:")
        print(f"USERBOT_SESSION_STRING={session_string}")
        print()
        print("⚠️  ВАЖНО: Эта строка даёт полный доступ к аккаунту!")
        print("    Храните её в безопасности!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nОтменено пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
