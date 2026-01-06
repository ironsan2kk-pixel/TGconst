#!/usr/bin/env python3
"""
Точка входа для запуска Backend API
"""
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from app.config import get_settings


def main():
    """Запуск сервера"""
    settings = get_settings()
    
    print("=" * 50)
    print("🤖 Telegram Bot Constructor API")
    print("=" * 50)
    print(f"Host: {settings.BACKEND_HOST}")
    print(f"Port: {settings.BACKEND_PORT}")
    print(f"Debug: {settings.DEBUG}")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )


if __name__ == "__main__":
    main()
