"""Tests for JWT authentication."""
import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_login_returns_tokens(client: AsyncClient) -> None:
    """Login with valid credentials returns access and refresh tokens."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": settings.ADMIN_USERNAME,
            "password": settings.ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient) -> None:
    """Login with wrong credentials returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient) -> None:
    """Admin endpoint without token returns 401."""
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "A test project description that is long enough",
            "stack": ["Python", "FastAPI"],
            "status": "done",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient) -> None:
    """Admin endpoint with invalid token returns 401."""
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "A test project description that is long enough",
            "stack": ["Python", "FastAPI"],
            "status": "done",
        },
        headers={"Authorization": "Bearer invalid-token-here"},
    )
    assert response.status_code == 401
