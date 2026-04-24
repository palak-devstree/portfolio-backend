"""SystemDesign SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text

from app.core.database import Base


class SystemDesign(Base):
    """System design case study model."""

    __tablename__ = "system_designs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    stack = Column(ARRAY(String), nullable=False)
    notes = Column(ARRAY(Text), nullable=False)
    diagram_url = Column(String(500), nullable=True)
    diagram_type = Column(String(50), nullable=True)
    complexity_level = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<SystemDesign id={self.id} title={self.title!r} level={self.complexity_level}>"
