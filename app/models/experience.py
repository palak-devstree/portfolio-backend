"""Experience SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text

from app.core.database import Base


class Experience(Base):
    """Experience model - stores work experience and roles."""

    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    company_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)  # e.g. "Jan 2020"
    end_date = Column(String(50), nullable=True)    # e.g. "Present"
    description = Column(Text, nullable=True)  # Legacy single text field
    description_points = Column(ARRAY(String), nullable=False, default=[])  # List of bullet points
    technologies = Column(ARRAY(String), nullable=False, default=[])
    project_urls = Column(ARRAY(String), nullable=False, default=[])
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Experience id={self.id} company={self.company!r} position={self.position!r}>"
