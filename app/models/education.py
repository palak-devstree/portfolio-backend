"""Education SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text

from app.core.database import Base


class Education(Base):
    """Education model - stores academic qualifications."""

    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)  # e.g. "2018" or "Sep 2018"
    end_date = Column(String(50), nullable=True)    # e.g. "2022" or "Present"
    description = Column(Text, nullable=True)  # Legacy single text field
    description_points = Column(ARRAY(String), nullable=False, default=[])  # List of bullet points
    location = Column(String(255), nullable=True)
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
        return f"<Education id={self.id} institution={self.institution!r}>"
