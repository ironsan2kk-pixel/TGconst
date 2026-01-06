"""Database connection and session management."""

import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models import Base


# Get database path from environment or use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/bot.db")

# Ensure data directory exists
db_path = Path(DATABASE_PATH)
db_path.parent.mkdir(parents=True, exist_ok=True)

# Create async engine
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

# Create session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
