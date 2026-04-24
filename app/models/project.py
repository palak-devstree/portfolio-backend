"""Project SQLAlchemy model."""
import enum
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Enum, Integer, String, Text

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    BUILDING = "building"
    DONE = "done"
    PLANNED = "planned"
    EXPLORING = "exploring"


class Project(Base):
    """Portfolio project model."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    stack = Column(ARRAY(String), nullable=False)
    status = Column(
        Enum(ProjectStatus, name="projectstatus", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProjectStatus.PLANNED,
    )
    github_url = Column(String(500), nullable=True)
    details_url = Column(String(500), nullable=True)
    github_stars = Column(Integer, default=0, nullable=False)
    github_forks = Column(Integer, default=0, nullable=False)
    last_commit_date = Column(DateTime, nullable=True)
    featured = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} status={self.status}>"
