"""
Admin Panel - FastAPI Application
Точка входа для запуска админ-панели
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Добавляем корень проекта в path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from admin.config import settings
from admin.database import check_database
from admin.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    print("=" * 50)
    print("🚀 Admin Panel Starting...")
    print(f"📁 Database: {settings.DATABASE_PATH}")
    print(f"🔧 Debug: {settings.DEBUG}")
    print("=" * 50)
    
    # Проверка БД
    db_ok = await check_database()
    if db_ok:
        print("✅ Database connected")
    else:
        print("❌ Database connection failed!")
    
    yield
    
    # Shutdown
    print("👋 Admin Panel Shutting down...")


# Создание приложения
app = FastAPI(
    title="Telegram Channel Bot - Admin Panel",
    description="API для управления Telegram ботом продажи доступа к каналам",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутера
app.include_router(api_router)


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """Проверка состояния сервера"""
    db_status = await check_database()
    return {
        "status": "ok" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0",
    }


@app.get("/", tags=["System"])
async def root():
    """Корневой endpoint"""
    return {
        "message": "Telegram Channel Bot - Admin API",
        "docs": "/docs",
        "health": "/health",
    }


def main():
    """Запуск сервера"""
    uvicorn.run(
        "admin.run:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
