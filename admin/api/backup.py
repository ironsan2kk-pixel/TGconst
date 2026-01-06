"""Backup API endpoints."""

import os
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from admin.config import settings

router = APIRouter()

# Paths
DATA_DIR = Path(settings.DATABASE_PATH).parent
BACKUP_DIR = DATA_DIR / "backups"
DB_FILE = Path(settings.DATABASE_PATH)


def ensure_backup_dir():
    """Ensure backup directory exists."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def get_backup_files() -> list[dict]:
    """Get list of backup files."""
    ensure_backup_dir()
    
    files = []
    for f in BACKUP_DIR.glob("*.db"):
        stat = f.stat()
        files.append({
            "filename": f.name,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    # Sort by date descending
    files.sort(key=lambda x: x["created_at"], reverse=True)
    return files


@router.get("")
async def list_backups():
    """List all available backups."""
    files = get_backup_files()
    
    # Get database size
    db_size = DB_FILE.stat().st_size if DB_FILE.exists() else 0
    
    return {
        "database_size": db_size,
        "backup_dir": str(BACKUP_DIR),
        "backups": files
    }


@router.post("")
async def create_backup():
    """Create a new backup."""
    ensure_backup_dir()
    
    if not DB_FILE.exists():
        raise HTTPException(status_code=404, detail="Database file not found")
    
    # Generate backup filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"bot_backup_{timestamp}.db"
    backup_path = BACKUP_DIR / backup_filename
    
    try:
        # Copy database file
        shutil.copy2(DB_FILE, backup_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")
    
    return {
        "status": "ok",
        "message": "Backup created successfully",
        "filename": backup_filename,
        "size": backup_path.stat().st_size,
        "path": str(backup_path)
    }


@router.get("/download/{filename}")
async def download_backup(filename: str):
    """Download a backup file."""
    # Validate filename (prevent path traversal)
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    backup_path = BACKUP_DIR / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup not found")
    
    return FileResponse(
        path=backup_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.post("/restore/{filename}")
async def restore_backup(filename: str):
    """Restore database from backup."""
    # Validate filename (prevent path traversal)
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    backup_path = BACKUP_DIR / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup not found")
    
    try:
        # Create backup of current database before restore
        if DB_FILE.exists():
            pre_restore_backup = BACKUP_DIR / f"pre_restore_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(DB_FILE, pre_restore_backup)
        
        # Restore from backup
        shutil.copy2(backup_path, DB_FILE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")
    
    return {
        "status": "ok",
        "message": "Database restored successfully. Please restart the application.",
        "restored_from": filename
    }


@router.delete("/{filename}")
async def delete_backup(filename: str):
    """Delete a backup file."""
    # Validate filename (prevent path traversal)
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    backup_path = BACKUP_DIR / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup not found")
    
    try:
        backup_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
    
    return {
        "status": "ok",
        "message": "Backup deleted successfully",
        "filename": filename
    }


@router.post("/cleanup")
async def cleanup_old_backups(keep_last: int = 5):
    """Delete old backups, keeping only the last N."""
    files = get_backup_files()
    
    if len(files) <= keep_last:
        return {
            "status": "ok",
            "message": f"No cleanup needed. {len(files)} backups exist.",
            "deleted": []
        }
    
    # Files to delete (oldest ones)
    to_delete = files[keep_last:]
    deleted = []
    
    for f in to_delete:
        backup_path = BACKUP_DIR / f["filename"]
        try:
            backup_path.unlink()
            deleted.append(f["filename"])
        except Exception:
            pass
    
    return {
        "status": "ok",
        "message": f"Deleted {len(deleted)} old backups",
        "deleted": deleted,
        "remaining": keep_last
    }
