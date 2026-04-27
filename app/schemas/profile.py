"""Profile Pydantic schemas."""
from datetime import datetime
from typing import Any, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, field_validator


class SkillCategory(BaseModel):
    """A named category containing a list of skill strings."""
    category: str = Field(..., min_length=1, max_length=100)
    skills: List[str] = Field(default_factory=list)


class ProfileBase(BaseModel):
    """Base profile schema with common fields."""

    full_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    tagline: str = Field(..., min_length=1, max_length=500)
    years_of_experience: int = Field(..., ge=0)
    professional_summary: str = Field(..., min_length=1)
    skills: List[SkillCategory] = Field(default_factory=list)

    @field_validator("skills", mode="before")
    @classmethod
    def coerce_skills(cls, v: Any) -> List[Any]:
        """
        Accept both legacy flat string lists and the current SkillCategory format.
        ['Python', 'Go'] → [{'category': 'Skills', 'skills': ['Python', 'Go']}]
        """
        if not isinstance(v, list):
            return v
        if v and isinstance(v[0], str):
            return [{"category": "Skills", "skills": v}]
        return v
    
    # Contact & Links
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    resume_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    
    # Page Visibility
    show_blog: bool = False
    show_projects: bool = True
    show_system_designs: bool = False
    show_lab: bool = False
    show_about: bool = True
    show_education: bool = True
    show_certificates: bool = True
    show_experience: bool = True
    
    # Current Focus
    current_learning: List[str] = Field(default_factory=list)
    current_building: List[str] = Field(default_factory=list)
    current_exploring: List[str] = Field(default_factory=list)

    # Site Copy
    navbar_brand: Optional[str] = Field(None, max_length=255)
    hero_badge: Optional[str] = Field(None, max_length=255)
    hero_cluster_label: Optional[str] = Field(None, max_length=255)
    subtitle_projects: Optional[str] = Field(None, max_length=255)
    subtitle_writing: Optional[str] = Field(None, max_length=255)
    subtitle_designs: Optional[str] = Field(None, max_length=255)
    subtitle_lab: Optional[str] = Field(None, max_length=255)
    subtitle_about: Optional[str] = Field(None, max_length=255)
    subtitle_contact: Optional[str] = Field(None, max_length=255)
    contact_response_note: Optional[str] = Field(None, max_length=255)
    
    # About section headings
    heading_learning: Optional[str] = Field(None, max_length=255)
    heading_building: Optional[str] = Field(None, max_length=255)
    heading_exploring: Optional[str] = Field(None, max_length=255)


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
    skills: Optional[List[SkillCategory]] = None

    @field_validator("skills", mode="before")
    @classmethod
    def coerce_skills(cls, v: Any) -> Any:
        if not isinstance(v, list):
            return v
        if v and isinstance(v[0], str):
            return [{"category": "Skills", "skills": v}]
        return v
    
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    resume_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    
    show_blog: Optional[bool] = None
    show_projects: Optional[bool] = None
    show_system_designs: Optional[bool] = None
    show_lab: Optional[bool] = None
    show_about: Optional[bool] = None
    show_education: Optional[bool] = None
    show_certificates: Optional[bool] = None
    show_experience: Optional[bool] = None
    
    current_learning: Optional[List[str]] = None
    current_building: Optional[List[str]] = None
    current_exploring: Optional[List[str]] = None

    # Site Copy
    navbar_brand: Optional[str] = Field(None, max_length=255)
    hero_badge: Optional[str] = Field(None, max_length=255)
    hero_cluster_label: Optional[str] = Field(None, max_length=255)
    subtitle_projects: Optional[str] = Field(None, max_length=255)
    subtitle_writing: Optional[str] = Field(None, max_length=255)
    subtitle_designs: Optional[str] = Field(None, max_length=255)
    subtitle_lab: Optional[str] = Field(None, max_length=255)
    subtitle_about: Optional[str] = Field(None, max_length=255)
    subtitle_contact: Optional[str] = Field(None, max_length=255)
    contact_response_note: Optional[str] = Field(None, max_length=255)
    
    # About section headings
    heading_learning: Optional[str] = Field(None, max_length=255)
    heading_building: Optional[str] = Field(None, max_length=255)
    heading_exploring: Optional[str] = Field(None, max_length=255)


class ProfileResponse(ProfileBase):
    """Schema for profile responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
