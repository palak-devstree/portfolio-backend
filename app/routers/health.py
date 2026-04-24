"""Health check endpoint for UptimeRobot keep-alive pings."""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache
from app.core.database import get_db
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> dict:
    """
    Health check endpoint for UptimeRobot keep-alive pings.
    Render free tier spins down after 15min idle — ping every 10min prevents this.
    Returns HTTP 200 in both healthy and degraded states (never 5xx).
    """
    db = DatabaseService(session)
    db_ok = await db.ping()
    cache_ok = await cache.ping()

    status = "healthy" if (db_ok and cache_ok) else "degraded"

    return {
        "status": status,
        "database": "ok" if db_ok else "unavailable",
        "cache": "ok" if cache_ok else "unavailable",
        "timestamp": datetime.utcnow().isoformat(),
    }
