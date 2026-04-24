"""BlogPost SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base


class BlogPost(Base):
    """Blog post model."""

    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    preview = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    published_date = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=True)
    read_time_minutes = Column(Integer, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    meta_description = Column(String(160), nullable=True)
    meta_keywords = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<BlogPost id={self.id} slug={self.slug!r} published={self.is_published}>"
