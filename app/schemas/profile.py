"""Profile Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ProfileBase(BaseModel):
    """Base profile schema with common fields."""

    full_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    tagline: str = Field(..., min_length=1, max_length=500)
    years_of_experience: int = Field(..., ge=0)
    professional_summary: str = Field(..., min_length=1)
    skills: List[str] = Field(default_factory=list)
    
    # Contact & Links
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    resume_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    
    # Page Visibility
    show_blog: bool = True
    show_projects: bool = True
    show_system_designs: bool = True
    show_lab: bool = True
    show_about: bool = True
    
    # Current Focus
    current_learning: List[str] = Field(default_factory=list)
    current_building: List[str] = Field(default_factory=list)
    current_exploring: List[str] = Field(default_factory=list)


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""
    pass


class ProfileUpdate(BaseModel):
    """Schema for updating a profile (all fields optional)."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, min_length=1, max_length=255)
    tagline: Optional[str] = Field(None, min_length=1, max_length=500)
    years_of_experience: Optional[int] = Field(None, ge=0)
    professional_summary: Optional[str] = Field(None, min_length=1)
    skills: Optional[List[str]] = None
    
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    resume_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    
    show_blog: Optional[bool] = None
    show_projects: Optional[bool] = None
    show_system_designs: Optional[bool] = None
    show_lab: Optional[bool] = None
    show_about: Optional[bool] = None
    
    current_learning: Optional[List[str]] = None
    current_building: Optional[List[str]] = None
    current_exploring: Optional[List[str]] = None


class ProfileResponse(ProfileBase):
    """Schema for profile responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
