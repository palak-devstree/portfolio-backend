"""Projects REST API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.analytics import track_event
from app.services.cache import CacheService
from app.services.database import DatabaseService
from fastapi import Request

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    request: Request,
    background_tasks: BackgroundTasks,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[ProjectStatus] = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> List[ProjectResponse]:
    """
    List projects with pagination and optional status filter.
    Results ordered by display_order ASC, then created_at DESC.
    Cached for 5 minutes.
    """
    cache_key = f"projects:list:{skip}:{limit}:{status_filter}"
    cached = await cache.get(cache_key)
    if cached:
        import json
        return [ProjectResponse(**p) for p in json.loads(cached)]

    db = DatabaseService(session)
    filters = {"status": status_filter} if status_filter else None
    projects = await db.get_all(
        Project,
        skip=skip,
        limit=limit,
        filters=filters,
        order_by=[asc(Project.display_order), desc(Project.created_at)],
    )

    response = [ProjectResponse.model_validate(p) for p in projects]
    await cache.set(cache_key, [r.model_dump(mode="json") for r in response], ttl=CACHE_TTL)

    background_tasks.add_task(
        track_event, session, "page_view", request, "project", None
    )
    return response


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Get a single project by ID."""
    db = DatabaseService(session)
    project = await db.get_by_id(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    background_tasks.add_task(
        track_event, session, "page_view", request, "project", project_id
    )
    return ProjectResponse.model_validate(project)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> ProjectResponse:
    """Create a new project. Admin only."""
    db = DatabaseService(session)

    # Check uniqueness
    existing = await db.get_by_field(Project, "name", project_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project_data.name}' already exists",
        )

    project = Project(**project_data.model_dump())
    created = await db.create(project)
    await cache.invalidate_pattern("projects:*")
    logger.info("project_created", project_id=created.id, name=created.name)
    return ProjectResponse.model_validate(created)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> ProjectResponse:
    """Update an existing project. Admin only."""
    db = DatabaseService(session)
    project = await db.get_by_id(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    update_data = project_data.model_dump(exclude_unset=True)
    updated = await db.update(project, update_data)
    await cache.invalidate_pattern("projects:*")
    logger.info("project_updated", project_id=project_id)
    return ProjectResponse.model_validate(updated)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete a project. Admin only."""
    db = DatabaseService(session)
    project = await db.get_by_id(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    await db.delete(project)
    await cache.invalidate_pattern("projects:*")
    logger.info("project_deleted", project_id=project_id)
