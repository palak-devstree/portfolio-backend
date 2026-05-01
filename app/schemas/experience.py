"""Experience Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ExperienceBase(BaseModel):
    """Base experience schema with common fields."""

    company: str = Field(..., min_length=1, max_length=255)
    position: str = Field(..., min_length=1, max_length=255)
    company_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)
    start_date: Optional[str] = Field(None, max_length=50)
    end_date: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None  # Legacy field
    description_points: List[str] = Field(default_factory=list)  # Preferred: list of bullet points
    technologies: List[str] = Field(default_factory=list)
    project_urls: List[str] = Field(default_factory=list)
    image_url: Optional[str] = Field(None, max_length=500)
    display_order: int = Field(default=0, ge=0)


class ExperienceCreate(ExperienceBase):
    """Schema for creating experience."""
    pass


class ExperienceUpdate(BaseModel):
    """Schema for updating experience (all fields optional)."""

    company: Optional[str] = Field(None, min_length=1, max_length=255)
    position: Optional[str] = Field(None, min_length=1, max_length=255)
    company_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)
    start_date: Optional[str] = Field(None, max_length=50)
    end_date: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    description_points: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    project_urls: Optional[List[str]] = None
    image_url: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = Field(None, ge=0)


class ExperienceResponse(ExperienceBase):
    """Schema for experience responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
