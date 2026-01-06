"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from bot.database import init_db, engine
from bot.models import Base


async def main():
    """Initialize database."""
    print("🗄️  Initializing database...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized successfully!")
    print(f"📁 Database file: {engine.url}")
    
    # Print created tables
    print("\n📋 Created tables:")
    for table in Base.metadata.tables:
        print(f"   - {table}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
