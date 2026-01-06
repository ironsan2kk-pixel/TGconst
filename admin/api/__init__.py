"""API routes."""

from fastapi import APIRouter

from admin.api import webhooks, broadcasts

# Main router
router = APIRouter()

# Include webhook routes
router.include_router(webhooks.router)

# Include broadcast routes
router.include_router(broadcasts.router)


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    from ..database import check_db_connection
    
    db_ok = await check_db_connection()
    
    return {
        "status": "ok" if db_ok else "error",
        "database": "connected" if db_ok else "disconnected"
    }
