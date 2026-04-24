"""Profile endpoints — public profile info and admin management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["profile"])
logger = get_logger(__name__)


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(session: AsyncSession = Depends(get_db)) -> ProfileResponse:
    """
    Get public profile information.
    Returns the first (and should be only) profile record.
    """
    db = DatabaseService(session)
    profile = await db.get_first(Profile)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create one via admin panel.",
        )
    
    logger.info("profile_fetched", profile_id=profile.id)
    return profile


@router.post("/admin/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> ProfileResponse:
    """
    Create profile (admin only).
    Only one profile should exist - returns 400 if profile already exists.
    """
    db = DatabaseService(session)
    
    # Check if profile already exists
    existing = await db.get_first(Profile)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT /admin/profile to update.",
        )
    
    profile = Profile(**profile_data.model_dump())
    created = await db.create(profile)
    
    logger.info("profile_created", profile_id=created.id)
    return created


@router.put("/admin/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> ProfileResponse:
    """
    Update profile (admin only).
    Updates the first profile record.
    """
    db = DatabaseService(session)
    
    profile = await db.get_first(Profile)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Use POST /admin/profile to create.",
        )
    
    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)
    updated = await db.update(profile, update_data)
    
    logger.info("profile_updated", profile_id=updated.id)
    return updated


@router.delete("/admin/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> None:
    """
    Delete profile (admin only).
    Deletes the first profile record.
    """
    db = DatabaseService(session)
    
    profile = await db.get_first(Profile)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    
    await db.delete(profile)
    logger.info("profile_deleted", profile_id=profile.id)
