"""Profile endpoints — public profile info and admin management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["profile"])
logger = get_logger(__name__)


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(session: AsyncSession = Depends(get_db)) -> ProfileResponse:
    """
    Get public profile information.
    Returns the first (and should be only) profile record.
    If no profile exists in the database, returns fallback data.
    """
    db = DatabaseService(session)
    profile = await db.get_first(Profile)
    
    if not profile:
        logger.info("profile_not_found_returning_fallback")
        # Return fallback profile data when database is empty
        return ProfileResponse(
            id=1,
            full_name="Alex Chen",
            job_title="AI Backend Engineer",
            tagline="I build the systems behind AI products — LLM serving, RAG pipelines, and the distributed plumbing that keeps models fast, cheap, and correct in production.",
            years_of_experience=6,
            professional_summary="AI backend engineer focused on shipping ML systems that survive contact with real traffic. I design inference platforms, retrieval pipelines, and evaluation harnesses — the infrastructure layer between a model checkpoint and a product your users actually feel. My favorite deploys are the boring ones.",
            skills=[
                {
                    "category": "AI / ML",
                    "skills": ["PyTorch", "Transformers", "vLLM", "LangChain", "LlamaIndex", "Triton", "ONNX"],
                },
                {
                    "category": "Backend",
                    "skills": ["Python", "FastAPI", "Go", "Rust", "gRPC"],
                },
                {
                    "category": "Data & Storage",
                    "skills": ["PostgreSQL", "Redis", "Kafka", "Qdrant", "Pinecone"],
                },
                {
                    "category": "Infrastructure",
                    "skills": ["Kubernetes", "AWS", "GCP", "Docker"],
                },
            ],
            email="alex@alexchen.dev",
            phone="+1 (415) 555-0142",
            location="San Francisco, CA",
            resume_url="https://example.com/resume.pdf",
            github_url="https://github.com/alexchen",
            linkedin_url="https://linkedin.com/in/alexchen",
            twitter_url="https://twitter.com/alexchen",
            website_url="https://alexchen.dev",
            show_blog=False,
            show_projects=True,
            show_system_designs=False,
            show_lab=False,
            show_about=True,
            show_education=True,
            show_certificates=True,
            show_experience=True,
            current_learning=[
                "LLM fine-tuning and LoRA adapters",
                "Vector databases and hybrid retrieval",
                "Distributed tracing with OpenTelemetry",
                "Kubernetes operators in Go",
            ],
            current_building=[
                "Multi-tenant AI inference platform",
                "Real-time analytics pipeline over Kafka",
                "Distributed job queue with priority lanes",
                "Observability dashboard with SLO tracking",
            ],
            current_exploring=[
                "Rust for low-latency services",
                "eBPF for kernel-level observability",
                "WebAssembly on the edge",
                "Homomorphic encryption for private ML",
            ],
            navbar_brand="alex.ops",
            hero_badge="AI · Backend · Infra",
            hero_cluster_label="inference.cluster.us-west-2",
            subtitle_projects="backend systems, APIs, infrastructure",
            subtitle_writing="long-form notes on systems & engineering",
            subtitle_designs="architectures for real-world scale",
            subtitle_lab="experiments, benchmarks & research",
            subtitle_about="background, focus, stack",
            subtitle_contact="open inbox / fast reply",
            contact_response_note="responses usually within 72h",
            heading_learning="Currently Learning",
            heading_building="Currently Building",
            heading_exploring="Currently Exploring",
        )
    
    logger.info("profile_fetched", profile_id=profile.id)
    return profile


@router.post("/admin/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> ProfileResponse:
    """
    Create profile (admin only).
    Only one profile should exist - returns 400 if profile already exists.
    """
    db = DatabaseService(session)
    
    # Check if profile already exists
    existing = await db.get_first(Profile)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT /admin/profile to update.",
        )
    
    profile = Profile(**profile_data.model_dump())
    created = await db.create(profile)
    
    logger.info("profile_created", profile_id=created.id)
    return created


@router.put("/admin/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> ProfileResponse:
    """
    Update profile (admin only).
    Updates the first profile record.
    """
    db = DatabaseService(session)
    
    profile = await db.get_first(Profile)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Use POST /admin/profile to create.",
        )
    
    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)
    updated = await db.update(profile, update_data)
    
    logger.info("profile_updated", profile_id=updated.id)
    return updated


@router.delete("/admin/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> None:
    """
    Delete profile (admin only).
    Deletes the first profile record.
    """
    db = DatabaseService(session)
    
    profile = await db.get_first(Profile)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    
    await db.delete(profile)
    logger.info("profile_deleted", profile_id=profile.id)
