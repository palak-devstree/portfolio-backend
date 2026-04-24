"""Blog Post REST API endpoints."""
import json
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.blog_post import BlogPost
from app.schemas.blog_post import BlogPostCreate, BlogPostResponse, BlogPostUpdate
from app.services.analytics import track_event
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/blog", tags=["blog"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("", response_model=List[BlogPostResponse])
async def list_blog_posts(
    request: Request,
    background_tasks: BackgroundTasks,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    tag: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> List[BlogPostResponse]:
    """
    List published blog posts with pagination and optional tag filter.
    Only is_published=True posts are returned to public.
    """
    cache_key = f"blog:list:{skip}:{limit}:{tag}"
    cached = await cache.get(cache_key)
    if cached:
        return [BlogPostResponse(**p) for p in json.loads(cached)]

    db = DatabaseService(session)

    if tag:
        # Tag filtering requires a custom query
        from sqlalchemy import select
        from sqlalchemy.dialects.postgresql import array
        query = (
            select(BlogPost)
            .where(BlogPost.is_published == True)  # noqa: E712
            .where(BlogPost.tags.contains([tag]))
            .order_by(desc(BlogPost.published_date))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(query)
        posts = list(result.scalars().all())
    else:
        posts = await db.get_all(
            BlogPost,
            skip=skip,
            limit=limit,
            filters={"is_published": True},
            order_by=[desc(BlogPost.published_date)],
        )

    response = [BlogPostResponse.model_validate(p) for p in posts]
    await cache.set(cache_key, [r.model_dump(mode="json") for r in response], ttl=CACHE_TTL)

    background_tasks.add_task(track_event, session, "page_view", request, "blog", None)
    return response


@router.get("/{slug}", response_model=BlogPostResponse)
async def get_blog_post(
    slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
) -> BlogPostResponse:
    """Get a single blog post by slug. Increments views_count asynchronously."""
    db = DatabaseService(session)
    post = await db.get_by_field(BlogPost, "slug", slug)
    if not post or not post.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")

    # Increment views_count asynchronously (fire-and-forget)
    background_tasks.add_task(_increment_views, session, post.id)
    background_tasks.add_task(track_event, session, "page_view", request, "blog", post.id)

    return BlogPostResponse.model_validate(post)


async def _increment_views(session: AsyncSession, post_id: int) -> None:
    """Background task to increment blog post view count."""
    try:
        from sqlalchemy import update
        await session.execute(
            update(BlogPost)
            .where(BlogPost.id == post_id)
            .values(views_count=BlogPost.views_count + 1)
        )
        await session.commit()
    except Exception as exc:
        logger.warning("views_increment_failed", post_id=post_id, error=str(exc))


@router.post("", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    post_data: BlogPostCreate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> BlogPostResponse:
    """Create a new blog post. Admin only."""
    db = DatabaseService(session)

    existing = await db.get_by_field(BlogPost, "slug", post_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Blog post with slug '{post_data.slug}' already exists",
        )

    post = BlogPost(**post_data.model_dump())
    created = await db.create(post)
    await cache.invalidate_pattern("blog:*")
    logger.info("blog_post_created", post_id=created.id, slug=created.slug)
    return BlogPostResponse.model_validate(created)


@router.put("/{slug}", response_model=BlogPostResponse)
async def update_blog_post(
    slug: str,
    post_data: BlogPostUpdate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> BlogPostResponse:
    """Update a blog post by slug. Admin only."""
    db = DatabaseService(session)
    post = await db.get_by_field(BlogPost, "slug", slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")

    update_data = post_data.model_dump(exclude_unset=True)
    updated = await db.update(post, update_data)
    await cache.invalidate_pattern("blog:*")
    logger.info("blog_post_updated", slug=slug)
    return BlogPostResponse.model_validate(updated)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_post(
    slug: str,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete a blog post by slug. Admin only."""
    db = DatabaseService(session)
    post = await db.get_by_field(BlogPost, "slug", slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")

    await db.delete(post)
    await cache.invalidate_pattern("blog:*")
    logger.info("blog_post_deleted", slug=slug)
