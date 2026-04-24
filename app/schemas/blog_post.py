"""Pydantic schemas for BlogPost endpoints."""
import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BlogPostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    slug: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=100)
    preview: str = Field(..., min_length=50, max_length=500)
    tags: List[str] = Field(..., min_length=1, max_length=10)
    published_date: datetime
    read_time_minutes: int = Field(..., ge=1, le=120)
    is_published: bool = False
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[List[str]] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError("slug must be lowercase alphanumeric with hyphens only")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        if len(v) < 1 or len(v) > 10:
            raise ValueError("tags must contain 1-10 items")
        for tag in v:
            if len(tag) < 2 or len(tag) > 30:
                raise ValueError("each tag must be 2-30 characters")
        return v


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    slug: Optional[str] = None
    content: Optional[str] = Field(None, min_length=100)
    preview: Optional[str] = Field(None, min_length=50, max_length=500)
    tags: Optional[List[str]] = None
    published_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    read_time_minutes: Optional[int] = Field(None, ge=1, le=120)
    is_published: Optional[bool] = None
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[List[str]] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError("slug must be lowercase alphanumeric with hyphens only")
        return v


class BlogPostResponse(BlogPostBase):
    id: int
    views_count: int
    updated_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
