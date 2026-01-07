"""Admin panel API server."""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from bot.config import config
from bot.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    print("🚀 Starting Admin API...")
    config.ensure_dirs()
    await init_db()
    print("✅ Database connected")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_db()
    print("✅ Database closed")


# Create FastAPI app
app = FastAPI(
    title="Telegram Channel Bot Admin API",
    description="Admin panel API for managing the Telegram bot",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Telegram Channel Bot Admin API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": config.database_path,
    }


@app.get("/api/status")
async def api_status():
    """API status with detailed info."""
    return {
        "status": "running",
        "debug": config.debug,
        "timestamp": datetime.utcnow().isoformat(),
    }


def main():
    """Run the admin API server."""
    print(f"""
╔════════════════════════════════════════════╗
║     Telegram Channel Bot - Admin API       ║
╠════════════════════════════════════════════╣
║  Host: {config.backend_host:<34} ║
║  Port: {config.backend_port:<34} ║
║  Debug: {str(config.debug):<33} ║
╚════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "admin.run:app",
        host=config.backend_host,
        port=config.backend_port,
        reload=config.debug,
    )


if __name__ == "__main__":
    main()
