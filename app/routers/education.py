"""Education REST API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.education import Education
from app.schemas.education import EducationCreate, EducationResponse, EducationUpdate
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/education", tags=["education"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("", response_model=List[EducationResponse])
async def list_education(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> List[EducationResponse]:
    """
    List education records with pagination.
    Results ordered by display_order ASC, then created_at DESC.
    Cached for 5 minutes.
    """
    cache_key = f"education:list:{skip}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        import json
        return [EducationResponse(**e) for e in json.loads(cached)]

    db = DatabaseService(session)
    education = await db.get_all(
        Education,
        skip=skip,
        limit=limit,
        order_by=[asc(Education.display_order), desc(Education.created_at)],
    )

    response = [EducationResponse.model_validate(e) for e in education]
    await cache.set(cache_key, [r.model_dump(mode="json") for r in response], ttl=CACHE_TTL)
    return response


@router.get("/{education_id}", response_model=EducationResponse)
async def get_education(
    education_id: int,
    session: AsyncSession = Depends(get_db),
) -> EducationResponse:
    """Get a single education record by ID."""
    db = DatabaseService(session)
    education = await db.get_by_id(Education, education_id)
    if not education:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
    return EducationResponse.model_validate(education)


@router.post("", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def create_education(
    education_data: EducationCreate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> EducationResponse:
    """Create a new education record. Admin only."""
    db = DatabaseService(session)
    education = Education(**education_data.model_dump())
    created = await db.create(education)
    await cache.invalidate_pattern("education:*")
    logger.info("education_created", education_id=created.id, institution=created.institution)
    return EducationResponse.model_validate(created)


@router.put("/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: int,
    education_data: EducationUpdate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> EducationResponse:
    """Update an existing education record. Admin only."""
    db = DatabaseService(session)
    education = await db.get_by_id(Education, education_id)
    if not education:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")

    update_data = education_data.model_dump(exclude_unset=True)
    updated = await db.update(education, update_data)
    await cache.invalidate_pattern("education:*")
    logger.info("education_updated", education_id=education_id)
    return EducationResponse.model_validate(updated)


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: int,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete an education record. Admin only."""
    db = DatabaseService(session)
    education = await db.get_by_id(Education, education_id)
    if not education:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")

    await db.delete(education)
    await cache.invalidate_pattern("education:*")
    logger.info("education_deleted", education_id=education_id)
