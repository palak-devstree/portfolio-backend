"""Profile SQLAlchemy model - stores personal/professional information."""
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base


class Profile(Base):
    """
    Profile model - stores personal and professional information.
    Only one profile record should exist (singleton pattern).
    """

    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Info
    full_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    tagline = Column(String(500), nullable=False)
    
    # Professional Summary
    years_of_experience = Column(Integer, nullable=False, default=0)
    professional_summary = Column(Text, nullable=False)
    
    # Skills
    skills = Column(ARRAY(String), nullable=False, default=[])
    
    # Contact & Links
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    resume_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    
    # Page Visibility Flags
    show_blog = Column(Boolean, default=False, nullable=False)
    show_projects = Column(Boolean, default=True, nullable=False)
    show_system_designs = Column(Boolean, default=True, nullable=False)
    show_lab = Column(Boolean, default=False, nullable=False)
    show_about = Column(Boolean, default=True, nullable=False)
    
    # Current Focus (JSON-like arrays)
    current_learning = Column(ARRAY(String), nullable=False, default=[])
    current_building = Column(ARRAY(String), nullable=False, default=[])
    current_exploring = Column(ARRAY(String), nullable=False, default=[])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Profile id={self.id} name={self.full_name!r}>"
