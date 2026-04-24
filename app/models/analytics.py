"""Analytics SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, JSON, String

from app.core.database import Base


class Analytics(Base):
    """Analytics event tracking model."""

    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved in SQLAlchemy)

    # Composite index for resource lookups
    __table_args__ = (
        Index("ix_analytics_resource", "resource_type", "resource_id"),
    )

    def __repr__(self) -> str:
        return f"<Analytics id={self.id} event={self.event_type!r} ts={self.timestamp}>"
