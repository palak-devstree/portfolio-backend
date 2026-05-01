"""System Design REST API endpoints."""
import json
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.system_design import SystemDesign
from app.schemas.system_design import (
    SystemDesignCreate,
    SystemDesignResponse,
    SystemDesignUpdate,
)
from app.services.analytics import track_event
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/system-designs", tags=["system-designs"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("", response_model=List[SystemDesignResponse])
async def list_system_designs(
    request: Request,
    background_tasks: BackgroundTasks,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> List[SystemDesignResponse]:
    """List system designs with pagination."""
    cache_key = f"system_designs:list:{skip}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        return [SystemDesignResponse(**d) for d in json.loads(cached)]

    db = DatabaseService(session)
    designs = await db.get_all(
        SystemDesign,
        skip=skip,
        limit=limit,
        order_by=[desc(SystemDesign.created_at)],
    )

    response = [SystemDesignResponse.model_validate(d) for d in designs]
    await cache.set(cache_key, [r.model_dump(mode="json") for r in response], ttl=CACHE_TTL)

    background_tasks.add_task(track_event, session, "page_view", request, "system_design", None)
    return response


@router.get("/{design_id}", response_model=SystemDesignResponse)
async def get_system_design(
    design_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
) -> SystemDesignResponse:
    """Get a single system design by ID."""
    db = DatabaseService(session)
    design = await db.get_by_id(SystemDesign, design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System design not found"
        )

    background_tasks.add_task(
        track_event, session, "page_view", request, "system_design", design_id
    )
    return SystemDesignResponse.model_validate(design)


@router.post("", response_model=SystemDesignResponse, status_code=status.HTTP_201_CREATED)
async def create_system_design(
    design_data: SystemDesignCreate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> SystemDesignResponse:
    """Create a new system design. Admin only."""
    db = DatabaseService(session)
    design = SystemDesign(**design_data.model_dump())
    created = await db.create(design)
    await cache.invalidate_pattern("system_designs:*")
    logger.info("system_design_created", design_id=created.id)
    return SystemDesignResponse.model_validate(created)


@router.put("/{design_id}", response_model=SystemDesignResponse)
async def update_system_design(
    design_id: int,
    design_data: SystemDesignUpdate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> SystemDesignResponse:
    """Update a system design. Admin only."""
    db = DatabaseService(session)
    design = await db.get_by_id(SystemDesign, design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System design not found"
        )

    update_data = design_data.model_dump(exclude_unset=True)
    updated = await db.update(design, update_data)
    await cache.invalidate_pattern("system_designs:*")
    logger.info("system_design_updated", design_id=design_id)
    return SystemDesignResponse.model_validate(updated)


@router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_design(
    design_id: int,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete a system design and its associated Cloudinary image. Admin only."""
    db = DatabaseService(session)
    design = await db.get_by_id(SystemDesign, design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System design not found"
        )

    # Delete from Cloudinary if diagram_url exists
    if design.diagram_url:
        try:
            from app.services.cloudinary_service import CloudinaryService
            cloudinary_service = CloudinaryService()
            deleted = cloudinary_service.delete_by_url(design.diagram_url)
            if deleted:
                logger.info("cloudinary_image_deleted", design_id=design_id, url=design.diagram_url)
            else:
                logger.warning("cloudinary_image_not_deleted", design_id=design_id, url=design.diagram_url)
        except Exception as exc:
            # Don't fail the delete if Cloudinary cleanup fails
            logger.error("cloudinary_cleanup_failed", design_id=design_id, error=str(exc))

    # Delete from database
    await db.delete(design)
    await cache.invalidate_pattern("system_designs:*")
    logger.info("system_design_deleted", design_id=design_id)

