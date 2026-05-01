"""Education Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EducationBase(BaseModel):
    """Base education schema with common fields."""

    institution: str = Field(..., min_length=1, max_length=255)
    degree: str = Field(..., min_length=1, max_length=255)
    field_of_study: Optional[str] = Field(None, max_length=255)
    start_date: Optional[str] = Field(None, max_length=50)
    end_date: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None  # Legacy field
    description_points: List[str] = Field(default_factory=list)  # Preferred: list of bullet points
    location: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=500)
    display_order: int = Field(default=0, ge=0)


class EducationCreate(EducationBase):
    """Schema for creating education."""
    pass


class EducationUpdate(BaseModel):
    """Schema for updating education (all fields optional)."""

    institution: Optional[str] = Field(None, min_length=1, max_length=255)
    degree: Optional[str] = Field(None, min_length=1, max_length=255)
    field_of_study: Optional[str] = Field(None, max_length=255)
    start_date: Optional[str] = Field(None, max_length=50)
    end_date: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    description_points: Optional[List[str]] = None
    location: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = Field(None, ge=0)


class EducationResponse(EducationBase):
    """Schema for education responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
