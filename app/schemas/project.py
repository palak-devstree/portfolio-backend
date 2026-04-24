"""Pydantic schemas for Project endpoints."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10, max_length=5000)
    stack: List[str] = Field(..., min_length=1, max_length=20)
    status: ProjectStatus = ProjectStatus.PLANNED
    github_url: Optional[str] = None
    details_url: Optional[str] = None
    github_stars: int = Field(default=0, ge=0)
    github_forks: int = Field(default=0, ge=0)
    featured: bool = False
    display_order: int = 0

    @field_validator("stack")
    @classmethod
    def validate_stack(cls, v: List[str]) -> List[str]:
        if len(v) < 1 or len(v) > 20:
            raise ValueError("stack must contain 1-20 technologies")
        for tech in v:
            if len(tech) < 1 or len(tech) > 50:
                raise ValueError("each technology name must be 1-50 characters")
        return v

    @field_validator("github_url", "details_url", mode="before")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    stack: Optional[List[str]] = None
    status: Optional[ProjectStatus] = None
    github_url: Optional[str] = None
    details_url: Optional[str] = None
    github_stars: Optional[int] = Field(None, ge=0)
    github_forks: Optional[int] = Field(None, ge=0)
    featured: Optional[bool] = None
    display_order: Optional[int] = None
    last_commit_date: Optional[datetime] = None

    @field_validator("stack")
    @classmethod
    def validate_stack(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        if len(v) < 1 or len(v) > 20:
            raise ValueError("stack must contain 1-20 technologies")
        for tech in v:
            if len(tech) < 1 or len(tech) > 50:
                raise ValueError("each technology name must be 1-50 characters")
        return v


class ProjectResponse(ProjectBase):
    id: int
    last_commit_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
