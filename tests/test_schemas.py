"""Tests for Pydantic schema validation."""
import pytest
from pydantic import ValidationError

from app.schemas.project import ProjectCreate
from app.schemas.blog_post import BlogPostCreate
from app.schemas.system_design import SystemDesignCreate
from app.schemas.lab_experiment import LabExperimentCreate
from datetime import datetime


class TestProjectSchema:
    def test_valid_project(self) -> None:
        p = ProjectCreate(
            name="My Project",
            description="A detailed description of my project that is long enough",
            stack=["Python", "FastAPI"],
            status="done",
        )
        assert p.name == "My Project"

    def test_name_too_short(self) -> None:
        with pytest.raises(ValidationError):
            ProjectCreate(
                name="",
                description="A detailed description that is long enough",
                stack=["Python"],
                status="done",
            )

    def test_stack_too_many(self) -> None:
        with pytest.raises(ValidationError):
            ProjectCreate(
                name="Test",
                description="A detailed description that is long enough",
                stack=["tech"] * 21,  # 21 items, max is 20
                status="done",
            )

    def test_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            ProjectCreate(
                name="Test",
                description="A detailed description that is long enough",
                stack=["Python"],
                status="invalid_status",
            )

    def test_invalid_github_url(self) -> None:
        with pytest.raises(ValidationError):
            ProjectCreate(
                name="Test",
                description="A detailed description that is long enough",
                stack=["Python"],
                status="done",
                github_url="not-a-url",
            )

    def test_negative_stars(self) -> None:
        with pytest.raises(ValidationError):
            ProjectCreate(
                name="Test",
                description="A detailed description that is long enough",
                stack=["Python"],
                status="done",
                github_stars=-1,
            )


class TestBlogPostSchema:
    def test_valid_blog_post(self) -> None:
        post = BlogPostCreate(
            title="My Blog Post Title",
            slug="my-blog-post-title",
            content="A" * 100,
            preview="A" * 50,
            tags=["python", "fastapi"],
            published_date=datetime.utcnow(),
            read_time_minutes=5,
        )
        assert post.slug == "my-blog-post-title"

    def test_invalid_slug_uppercase(self) -> None:
        with pytest.raises(ValidationError):
            BlogPostCreate(
                title="My Blog Post",
                slug="My-Blog-Post",  # uppercase not allowed
                content="A" * 100,
                preview="A" * 50,
                tags=["python"],
                published_date=datetime.utcnow(),
                read_time_minutes=5,
            )

    def test_invalid_slug_spaces(self) -> None:
        with pytest.raises(ValidationError):
            BlogPostCreate(
                title="My Blog Post",
                slug="my blog post",  # spaces not allowed
                content="A" * 100,
                preview="A" * 50,
                tags=["python"],
                published_date=datetime.utcnow(),
                read_time_minutes=5,
            )

    def test_meta_description_too_long(self) -> None:
        with pytest.raises(ValidationError):
            BlogPostCreate(
                title="My Blog Post",
                slug="my-blog-post",
                content="A" * 100,
                preview="A" * 50,
                tags=["python"],
                published_date=datetime.utcnow(),
                read_time_minutes=5,
                meta_description="A" * 161,  # max is 160
            )


class TestSystemDesignSchema:
    def test_valid_system_design(self) -> None:
        sd = SystemDesignCreate(
            title="Distributed Cache System",
            description="A detailed description of the system design that is long enough",
            stack=["Redis", "Python"],
            notes=["Key point one that is long enough", "Key point two that is long enough"],
            complexity_level="intermediate",
        )
        assert sd.complexity_level == "intermediate"

    def test_invalid_complexity_level(self) -> None:
        with pytest.raises(ValidationError):
            SystemDesignCreate(
                title="Test Design",
                description="A detailed description that is long enough",
                stack=["Redis", "Python"],
                notes=["Note one that is long enough", "Note two that is long enough"],
                complexity_level="expert",  # not valid
            )

    def test_notes_too_short(self) -> None:
        with pytest.raises(ValidationError):
            SystemDesignCreate(
                title="Test Design",
                description="A detailed description that is long enough",
                stack=["Redis", "Python"],
                notes=["Only one note"],  # min is 2
                complexity_level="beginner",
            )
