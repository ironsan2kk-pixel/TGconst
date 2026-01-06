"""
FastAPI приложение - главная точка входа
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import get_main_engine, close_all_engines


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle события приложения"""
    settings = get_settings()
    
    # Startup
    print(f"🚀 Starting Bot Constructor API...")
    print(f"📁 Data directory: {settings.DATA_DIR.absolute()}")
    
    # Создаём папки
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.bots_dir.mkdir(parents=True, exist_ok=True)
    
    # Инициализируем главную БД (создаём движок)
    await get_main_engine()
    print(f"✅ Main database ready: {settings.MAIN_DB_PATH}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_all_engines()
    print("✅ All connections closed")


def create_app() -> FastAPI:
    """Фабрика создания приложения"""
    settings = get_settings()
    
    app = FastAPI(
        title="Telegram Bot Constructor API",
        description="API для управления конструктором Telegram-ботов",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Проверка работоспособности сервера"""
        return {"status": "ok"}
    
    @app.get("/", tags=["Health"])
    async def root():
        """Корневой эндпоинт"""
        return {
            "name": "Telegram Bot Constructor API",
            "version": "1.0.0",
            "status": "running"
        }
    
    return app


# Создаём приложение
app = create_app()
