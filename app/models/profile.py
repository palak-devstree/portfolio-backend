"""Profile SQLAlchemy model - stores personal/professional information."""
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

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
    
    # Skills — stored as [{category: str, skills: [str]}]
    skills = Column(JSONB, nullable=False, default=list)
    
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
    show_system_designs = Column(Boolean, default=False, nullable=False)
    show_lab = Column(Boolean, default=False, nullable=False)
    show_about = Column(Boolean, default=True, nullable=False)
    show_education = Column(Boolean, default=True, nullable=False)
    show_certificates = Column(Boolean, default=True, nullable=False)
    show_experience = Column(Boolean, default=True, nullable=False)
    
    # Current Focus (JSON-like arrays)
    current_learning = Column(ARRAY(String), nullable=False, default=[])
    current_building = Column(ARRAY(String), nullable=False, default=[])
    current_exploring = Column(ARRAY(String), nullable=False, default=[])

    # Site Copy — customisable strings shown on the public portfolio
    navbar_brand = Column(String(255), nullable=True, default='')
    hero_badge = Column(String(255), nullable=True, default='AI · Backend · Infra')
    hero_cluster_label = Column(String(255), nullable=True, default='inference.cluster.us-west-2')
    subtitle_projects = Column(String(255), nullable=True, default='backend systems, APIs, infrastructure')
    subtitle_writing = Column(String(255), nullable=True, default='long-form notes on systems & engineering')
    subtitle_designs = Column(String(255), nullable=True, default='architectures for real-world scale')
    subtitle_lab = Column(String(255), nullable=True, default='experiments, benchmarks & research')
    subtitle_about = Column(String(255), nullable=True, default='background, focus, stack')
    subtitle_contact = Column(String(255), nullable=True, default='open inbox / fast reply')
    contact_response_note = Column(String(255), nullable=True, default='responses usually within 72h')
    
    # About section headings
    heading_learning = Column(String(255), nullable=True, default='Currently Learning')
    heading_building = Column(String(255), nullable=True, default='Currently Building')
    heading_exploring = Column(String(255), nullable=True, default='Currently Exploring')
    
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
