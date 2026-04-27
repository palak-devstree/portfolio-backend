"""Experience REST API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.experience import Experience
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ExperienceUpdate
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/experience", tags=["experience"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("", response_model=List[ExperienceResponse])
async def list_experience(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> List[ExperienceResponse]:
    """
    List experience records with pagination.
    Results ordered by display_order ASC, then created_at DESC.
    Cached for 5 minutes.
    """
    cache_key = f"experience:list:{skip}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        import json
        return [ExperienceResponse(**e) for e in json.loads(cached)]

    db = DatabaseService(session)
    experience = await db.get_all(
        Experience,
        skip=skip,
        limit=limit,
        order_by=[asc(Experience.display_order), desc(Experience.created_at)],
    )

    response = [ExperienceResponse.model_validate(e) for e in experience]
    await cache.set(cache_key, [r.model_dump(mode="json") for r in response], ttl=CACHE_TTL)
    return response


@router.get("/{experience_id}", response_model=ExperienceResponse)
async def get_experience(
    experience_id: int,
    session: AsyncSession = Depends(get_db),
) -> ExperienceResponse:
    """Get a single experience record by ID."""
    db = DatabaseService(session)
    experience = await db.get_by_id(Experience, experience_id)
    if not experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    return ExperienceResponse.model_validate(experience)


@router.post("", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(
    experience_data: ExperienceCreate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> ExperienceResponse:
    """Create a new experience record. Admin only."""
    db = DatabaseService(session)
    experience = Experience(**experience_data.model_dump())
    created = await db.create(experience)
    await cache.invalidate_pattern("experience:*")
    logger.info("experience_created", experience_id=created.id, company=created.company)
    return ExperienceResponse.model_validate(created)


@router.put("/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: int,
    experience_data: ExperienceUpdate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> ExperienceResponse:
    """Update an existing experience record. Admin only."""
    db = DatabaseService(session)
    experience = await db.get_by_id(Experience, experience_id)
    if not experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")

    update_data = experience_data.model_dump(exclude_unset=True)
    updated = await db.update(experience, update_data)
    await cache.invalidate_pattern("experience:*")
    logger.info("experience_updated", experience_id=experience_id)
    return ExperienceResponse.model_validate(updated)


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    experience_id: int,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete an experience record. Admin only."""
    db = DatabaseService(session)
    experience = await db.get_by_id(Experience, experience_id)
    if not experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")

    await db.delete(experience)
    await cache.invalidate_pattern("experience:*")
    logger.info("experience_deleted", experience_id=experience_id)
