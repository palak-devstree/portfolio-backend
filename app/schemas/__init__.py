"""Pydantic schemas for request/response validation."""
from app.schemas.analytics import AnalyticsResponse
from app.schemas.auth import LoginRequest, TokenData, TokenResponse
from app.schemas.blog_post import BlogPostCreate, BlogPostResponse, BlogPostUpdate
from app.schemas.certificate import CertificateCreate, CertificateResponse, CertificateUpdate
from app.schemas.chatbot import ChatbotRequest, ChatbotResponse
from app.schemas.contact import (
    ContactMessageCreate,
    ContactMessageResponse,
    ContactMessageUpdate,
)
from app.schemas.dashboard import DashboardResponse
from app.schemas.education import EducationCreate, EducationResponse, EducationUpdate
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ExperienceUpdate
from app.schemas.lab_experiment import (
    LabExperimentCreate,
    LabExperimentResponse,
    LabExperimentUpdate,
)
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate, SkillCategory
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.system_design import (
    SystemDesignCreate,
    SystemDesignResponse,
    SystemDesignUpdate,
)

__all__ = [
    "AnalyticsResponse",
    "BlogPostCreate",
    "BlogPostResponse",
    "BlogPostUpdate",
    "CertificateCreate",
    "CertificateResponse",
    "CertificateUpdate",
    "ChatbotRequest",
    "ChatbotResponse",
    "ContactMessageCreate",
    "ContactMessageResponse",
    "ContactMessageUpdate",
    "DashboardResponse",
    "EducationCreate",
    "EducationResponse",
    "EducationUpdate",
    "ExperienceCreate",
    "ExperienceResponse",
    "ExperienceUpdate",
    "LabExperimentCreate",
    "LabExperimentResponse",
    "LabExperimentUpdate",
    "LoginRequest",
    "ProfileCreate",
    "ProfileResponse",
    "ProfileUpdate",
    "ProjectCreate",
    "ProjectResponse",
    "ProjectUpdate",
    "SkillCategory",
    "SystemDesignCreate",
    "SystemDesignResponse",
    "SystemDesignUpdate",
    "TokenData",
    "TokenResponse",
]
