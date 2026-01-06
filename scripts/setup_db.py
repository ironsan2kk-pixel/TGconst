"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from bot.database import init_db, engine, async_session_maker
from bot.models import Base
from sqlalchemy import text


async def migrate_menu_items():
    """Add new columns to menu_items if they don't exist."""
    async with async_session_maker() as session:
        # Check if photo_file_id column exists
        result = await session.execute(text("PRAGMA table_info(menu_items)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'photo_file_id' not in columns:
            print("   Adding column photo_file_id to menu_items...")
            await session.execute(text(
                "ALTER TABLE menu_items ADD COLUMN photo_file_id VARCHAR(255)"
            ))
            await session.commit()
            print("   ✓ Added photo_file_id")


async def main():
    """Initialize database."""
    print("🗄️  Initializing database...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized successfully!")
    print(f"📁 Database file: {engine.url}")
    
    # Run migrations
    print("\n🔄 Running migrations...")
    await migrate_menu_items()
    
    # Print created tables
    print("\n📋 Tables:")
    for table in Base.metadata.tables:
        print(f"   - {table}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
