#!/usr/bin/env python3
"""
Database Backup Script
Создание резервной копии базы данных
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Пути
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
DB_FILE = DATA_DIR / "bot.db"


def create_backup() -> str | None:
    """Создать бэкап базы данных"""
    
    # Проверка существования БД
    if not DB_FILE.exists():
        print(f"❌ Database not found: {DB_FILE}")
        return None
    
    # Создание директории для бэкапов
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Генерация имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"bot_backup_{timestamp}.db"
    backup_path = BACKUP_DIR / backup_name
    
    try:
        # Копирование файла
        shutil.copy2(DB_FILE, backup_path)
        
        # Получение размера
        size_bytes = backup_path.stat().st_size
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        
        print(f"✅ Backup created: {backup_name}")
        print(f"📁 Path: {backup_path}")
        print(f"📊 Size: {size_str}")
        
        return str(backup_path)
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None


def list_backups():
    """Показать список бэкапов"""
    
    if not BACKUP_DIR.exists():
        print("📁 No backups directory")
        return
    
    backups = sorted(BACKUP_DIR.glob("bot_backup_*.db"), reverse=True)
    
    if not backups:
        print("📁 No backups found")
        return
    
    print(f"\n📋 Backups ({len(backups)} total):")
    print("-" * 50)
    
    for backup in backups:
        size = backup.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  {backup.name}  ({size_str})  {mtime.strftime('%Y-%m-%d %H:%M')}")


def cleanup_old_backups(keep_last: int = 5):
    """Удалить старые бэкапы, оставив последние N"""
    
    if not BACKUP_DIR.exists():
        return
    
    backups = sorted(BACKUP_DIR.glob("bot_backup_*.db"), reverse=True)
    
    if len(backups) <= keep_last:
        print(f"📁 Only {len(backups)} backups, nothing to clean")
        return
    
    to_delete = backups[keep_last:]
    
    for backup in to_delete:
        try:
            backup.unlink()
            print(f"🗑️ Deleted: {backup.name}")
        except Exception as e:
            print(f"❌ Failed to delete {backup.name}: {e}")
    
    print(f"✅ Cleanup complete. Kept {keep_last} latest backups.")


def main():
    """Главная функция"""
    
    print("=" * 50)
    print("🗄️  Database Backup Tool")
    print("=" * 50)
    
    args = sys.argv[1:]
    
    if not args or args[0] == "create":
        create_backup()
    elif args[0] == "list":
        list_backups()
    elif args[0] == "cleanup":
        keep = int(args[1]) if len(args) > 1 else 5
        cleanup_old_backups(keep)
    else:
        print("""
Usage:
  python backup_db.py           - Create backup
  python backup_db.py create    - Create backup
  python backup_db.py list      - List all backups
  python backup_db.py cleanup N - Keep only N latest backups (default: 5)
""")


if __name__ == "__main__":
    main()
