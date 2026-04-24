"""Dashboard endpoint — aggregated statistics."""
import json
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.blog_post import BlogPost
from app.models.lab_experiment import LabExperiment
from app.models.project import Project, ProjectStatus
from app.models.system_design import SystemDesign
from app.schemas.dashboard import DashboardResponse
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["dashboard"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> DashboardResponse:
    """
    Get dashboard statistics.
    Cached for 5 minutes. Pre-warmed on application startup.
    """
    cache_key = "dashboard:metrics"
    cached = await cache.get(cache_key)
    if cached:
        logger.info("dashboard_cache_hit")
        return DashboardResponse(**json.loads(cached))

    db = DatabaseService(session)

    # Count resources
    projects_count = await db.count(Project, filters={"status": ProjectStatus.DONE})
    blog_posts_count = await db.count(BlogPost, filters={"is_published": True})
    system_designs_count = await db.count(SystemDesign)
    lab_experiments_count = await db.count(LabExperiment)

    # Default values (no longer using dashboard_metrics table)
    uptime_percentage = 99.9
    total_views = 0

    response = DashboardResponse(
        projects_count=projects_count,
        blog_posts_count=blog_posts_count,
        system_designs_count=system_designs_count,
        lab_experiments_count=lab_experiments_count,
        uptime_percentage=uptime_percentage,
        total_views=total_views,
        timestamp=datetime.utcnow(),
    )

    await cache.set(cache_key, response.model_dump(mode="json"), ttl=CACHE_TTL)
    logger.info("dashboard_cache_miss_refreshed")
    return response
