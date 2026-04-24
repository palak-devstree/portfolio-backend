"""Lab Experiment REST API endpoints."""
import json
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.lab_experiment import ExperimentStatus, LabExperiment
from app.schemas.lab_experiment import (
    LabExperimentCreate,
    LabExperimentResponse,
    LabExperimentUpdate,
)
from app.services.analytics import track_event
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/lab", tags=["lab"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("", response_model=List[LabExperimentResponse])
async def list_lab_experiments(
    request: Request,
    background_tasks: BackgroundTasks,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[ExperimentStatus] = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> List[LabExperimentResponse]:
    """List lab experiments with pagination and optional status filter."""
    cache_key = f"lab:list:{skip}:{limit}:{status_filter}"
    cached = await cache.get(cache_key)
    if cached:
        return [LabExperimentResponse(**e) for e in json.loads(cached)]

    db = DatabaseService(session)
    filters = {"status": status_filter} if status_filter else None
    experiments = await db.get_all(
        LabExperiment,
        skip=skip,
        limit=limit,
        filters=filters,
        order_by=[desc(LabExperiment.created_at)],
    )

    response = [LabExperimentResponse.model_validate(e) for e in experiments]
    await cache.set(cache_key, [r.model_dump(mode="json") for r in response], ttl=CACHE_TTL)

    background_tasks.add_task(track_event, session, "page_view", request, "lab", None)
    return response


@router.get("/{experiment_id}", response_model=LabExperimentResponse)
async def get_lab_experiment(
    experiment_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
) -> LabExperimentResponse:
    """Get a single lab experiment by ID."""
    db = DatabaseService(session)
    experiment = await db.get_by_id(LabExperiment, experiment_id)
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lab experiment not found"
        )

    background_tasks.add_task(
        track_event, session, "page_view", request, "lab", experiment_id
    )
    return LabExperimentResponse.model_validate(experiment)


@router.post("", response_model=LabExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_experiment(
    experiment_data: LabExperimentCreate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> LabExperimentResponse:
    """Create a new lab experiment. Admin only."""
    db = DatabaseService(session)
    experiment = LabExperiment(**experiment_data.model_dump())
    created = await db.create(experiment)
    await cache.invalidate_pattern("lab:*")
    logger.info("lab_experiment_created", experiment_id=created.id)
    return LabExperimentResponse.model_validate(created)


@router.put("/{experiment_id}", response_model=LabExperimentResponse)
async def update_lab_experiment(
    experiment_id: int,
    experiment_data: LabExperimentUpdate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> LabExperimentResponse:
    """Update a lab experiment. Admin only."""
    db = DatabaseService(session)
    experiment = await db.get_by_id(LabExperiment, experiment_id)
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lab experiment not found"
        )

    update_data = experiment_data.model_dump(exclude_unset=True)
    updated = await db.update(experiment, update_data)
    await cache.invalidate_pattern("lab:*")
    logger.info("lab_experiment_updated", experiment_id=experiment_id)
    return LabExperimentResponse.model_validate(updated)


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lab_experiment(
    experiment_id: int,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete a lab experiment. Admin only."""
    db = DatabaseService(session)
    experiment = await db.get_by_id(LabExperiment, experiment_id)
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lab experiment not found"
        )

    await db.delete(experiment)
    await cache.invalidate_pattern("lab:*")
    logger.info("lab_experiment_deleted", experiment_id=experiment_id)
