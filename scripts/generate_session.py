"""
Скрипт для генерации Pyrogram session string.

Запустите этот скрипт один раз, чтобы получить session string.
Затем добавьте его в .env файл как USERBOT_SESSION_STRING.
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Загружаем .env
load_dotenv()


async def main():
    """Генерация session string."""
    from pyrogram import Client
    
    print("=" * 50)
    print("  Pyrogram Session String Generator")
    print("=" * 50)
    print()
    
    # Получаем данные из .env или запрашиваем
    api_id = os.getenv('USERBOT_API_ID')
    api_hash = os.getenv('USERBOT_API_HASH')
    phone = os.getenv('USERBOT_PHONE')
    
    if not api_id or api_id == '12345678':
        print("API_ID not found in .env")
        api_id = input("Enter your API ID (from my.telegram.org): ").strip()
    
    if not api_hash or api_hash == 'your_api_hash':
        print("API_HASH not found in .env")
        api_hash = input("Enter your API HASH (from my.telegram.org): ").strip()
    
    if not phone or phone == '+79001234567':
        print("PHONE not found in .env")
        phone = input("Enter your phone number (with country code, e.g. +79001234567): ").strip()
    
    print()
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash[:10]}...")
    print(f"Phone: {phone}")
    print()
    
    # Создаём клиент
    print("Creating Pyrogram client...")
    
    async with Client(
        name="session_generator",
        api_id=int(api_id),
        api_hash=api_hash,
        phone_number=phone,
        in_memory=True,
    ) as client:
        # Получаем session string
        session_string = await client.export_session_string()
        
        print()
        print("=" * 50)
        print("  SUCCESS! Your session string:")
        print("=" * 50)
        print()
        print(session_string)
        print()
        print("=" * 50)
        print()
        print("Add this to your .env file as:")
        print(f"USERBOT_SESSION_STRING={session_string}")
        print()
        
        # Предлагаем автоматически обновить .env
        update = input("Update .env file automatically? (y/n): ").strip().lower()
        
        if update == 'y':
            env_path = Path(__file__).parent.parent / '.env'
            
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем и заменяем USERBOT_SESSION_STRING
                import re
                if 'USERBOT_SESSION_STRING=' in content:
                    content = re.sub(
                        r'USERBOT_SESSION_STRING=.*',
                        f'USERBOT_SESSION_STRING={session_string}',
                        content
                    )
                else:
                    content += f'\nUSERBOT_SESSION_STRING={session_string}\n'
                
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print()
                print("✅ .env file updated successfully!")
            else:
                print()
                print("❌ .env file not found. Please update manually.")
        
        print()
        print("You can now run start_userbot.bat")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
