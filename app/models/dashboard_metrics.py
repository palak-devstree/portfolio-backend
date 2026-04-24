"""DashboardMetrics SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer

from app.core.database import Base


class DashboardMetrics(Base):
    """Daily aggregated dashboard metrics model."""

    __tablename__ = "dashboard_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    projects_count = Column(Integer, default=0, nullable=False)
    blog_posts_count = Column(Integer, default=0, nullable=False)
    system_designs_count = Column(Integer, default=0, nullable=False)
    lab_experiments_count = Column(Integer, default=0, nullable=False)
    total_views = Column(Integer, default=0, nullable=False)
    api_requests_count = Column(Integer, default=0, nullable=False)
    uptime_percentage = Column(Float, default=100.0, nullable=False)
    avg_response_time_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<DashboardMetrics date={self.date} projects={self.projects_count}>"
