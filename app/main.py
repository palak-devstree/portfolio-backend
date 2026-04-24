"""
Portfolio Backend — FastAPI Application Entry Point.

Architecture:
- FastAPI with async SQLAlchemy (Neon PostgreSQL)
- Upstash Redis for caching
- Google Gemini API for AI chatbot
- UptimeRobot pings /health every 10min to prevent Render spindown
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import setup_middleware

# Configure structured logging before anything else
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.
    On startup: run migrations, warm dashboard cache.
    On shutdown: close Redis connection.
    """
    logger.info("application_starting", environment=settings.ENVIRONMENT)

    # Run Alembic migrations on startup
    await _run_migrations()

    # Pre-warm dashboard cache to avoid slow first response after cold start
    await _warm_cache()

    logger.info("application_ready")
    yield

    # Cleanup on shutdown
    from app.core.cache import close_redis
    await close_redis()
    logger.info("application_shutdown")


async def _run_migrations() -> None:
    """Run Alembic migrations programmatically on startup."""
    try:
        import asyncio
        from alembic import command
        from alembic.config import Config

        def run_upgrade() -> None:
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_upgrade)
        logger.info("migrations_applied")
    except Exception as exc:
        logger.warning("migrations_failed", error=str(exc))


async def _warm_cache() -> None:
    """Pre-populate dashboard cache on startup."""
    try:
        from app.core.cache import get_redis_client
        from app.core.database import AsyncSessionLocal
        from app.services.cache import CacheService

        async with AsyncSessionLocal() as session:
            cache = CacheService(get_redis_client())
            # Import here to avoid circular imports
            from app.routers.dashboard import get_dashboard
            from app.core.cache import get_cache

            # Trigger dashboard data fetch which will populate cache
            from app.models.blog_post import BlogPost
            from app.models.lab_experiment import LabExperiment
            from app.models.project import Project, ProjectStatus
            from app.models.system_design import SystemDesign
            from app.schemas.dashboard import DashboardResponse
            from app.services.database import DatabaseService
            from datetime import datetime
            import json

            db = DatabaseService(session)
            cache_key = "dashboard:metrics"

            projects_count = await db.count(Project, filters={"status": ProjectStatus.DONE})
            blog_posts_count = await db.count(BlogPost, filters={"is_published": True})
            system_designs_count = await db.count(SystemDesign)
            lab_experiments_count = await db.count(LabExperiment)

            response = DashboardResponse(
                projects_count=projects_count,
                blog_posts_count=blog_posts_count,
                system_designs_count=system_designs_count,
                lab_experiments_count=lab_experiments_count,
                uptime_percentage=99.9,
                total_views=0,
                timestamp=datetime.utcnow(),
            )
            await cache.set(cache_key, response.model_dump(mode="json"), ttl=300)
            logger.info("cache_warmed", key=cache_key)

    except Exception as exc:
        # Cache warming failure must not prevent startup
        logger.warning("cache_warm_failed", error=str(exc))


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI instance."""
    app = FastAPI(
        title="Portfolio Backend API",
        description=(
            "FastAPI backend for AI Backend Engineer portfolio. "
            "Built on free-tier cloud services: Neon PostgreSQL, Upstash Redis, Gemini API."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Register middleware (order matters — CORS outermost)
    setup_middleware(app)

    # Register routers
    _register_routers(app)

    # Register exception handlers
    _register_exception_handlers(app)

    return app


def _register_routers(app: FastAPI) -> None:
    """Register all API routers."""
    from app.routers import (
        auth,
        blog,
        chatbot,
        contact,
        dashboard,
        health,
        lab,
        profile,
        projects,
        system_designs,
        uploads,
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(profile.router)
    app.include_router(projects.router)
    app.include_router(blog.router)
    app.include_router(system_designs.router)
    app.include_router(lab.router)
    app.include_router(chatbot.router)
    app.include_router(uploads.router)
    app.include_router(contact.router)


def _register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers for consistent JSON error responses."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Return structured 422 responses for Pydantic validation errors."""
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "message": "Request validation failed",
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc) -> JSONResponse:
        logger.error("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


# Create the application instance
app = create_app()
