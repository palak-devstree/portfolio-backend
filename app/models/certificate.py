"""Certificate SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.core.database import Base


class Certificate(Base):
    """Certificate model - stores professional certifications and credentials."""

    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    issue_date = Column(String(50), nullable=True)  # e.g. "Jan 2023"
    expiry_date = Column(String(50), nullable=True)
    credential_id = Column(String(255), nullable=True)
    credential_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Certificate id={self.id} title={self.title!r}>"
