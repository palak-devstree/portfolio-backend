"""Pydantic schemas for Dashboard endpoint."""
from datetime import datetime

from pydantic import BaseModel, Field


class DashboardResponse(BaseModel):
    projects_count: int = Field(..., ge=0)
    blog_posts_count: int = Field(..., ge=0)
    system_designs_count: int = Field(..., ge=0)
    lab_experiments_count: int = Field(..., ge=0)
    uptime_percentage: float = Field(..., ge=0.0, le=100.0)
    total_views: int = Field(..., ge=0)
    timestamp: datetime
