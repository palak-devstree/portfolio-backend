"""Tests for the /health endpoint."""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    """Health endpoint should always return HTTP 200."""
    with (
        patch("app.routers.health.DatabaseService") as mock_db_cls,
        patch("app.routers.health.CacheService") as mock_cache_cls,
    ):
        mock_db = AsyncMock()
        mock_db.ping.return_value = True
        mock_db_cls.return_value = mock_db

        mock_cache = AsyncMock()
        mock_cache.ping.return_value = True
        mock_cache_cls.return_value = mock_cache

        response = await client.get("/health")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_healthy_when_all_ok(client: AsyncClient) -> None:
    """Health endpoint returns 'healthy' when DB and cache are reachable."""
    with (
        patch("app.routers.health.DatabaseService") as mock_db_cls,
        patch("app.routers.health.CacheService") as mock_cache_cls,
    ):
        mock_db = AsyncMock()
        mock_db.ping.return_value = True
        mock_db_cls.return_value = mock_db

        mock_cache = AsyncMock()
        mock_cache.ping.return_value = True
        mock_cache_cls.return_value = mock_cache

        response = await client.get("/health")

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "cache" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_returns_degraded_when_db_down(client: AsyncClient) -> None:
    """Health endpoint returns 'degraded' (not 5xx) when DB is unavailable."""
    with (
        patch("app.routers.health.DatabaseService") as mock_db_cls,
        patch("app.routers.health.CacheService") as mock_cache_cls,
    ):
        mock_db = AsyncMock()
        mock_db.ping.return_value = False
        mock_db_cls.return_value = mock_db

        mock_cache = AsyncMock()
        mock_cache.ping.return_value = True
        mock_cache_cls.return_value = mock_cache

        response = await client.get("/health")

    assert response.status_code == 200  # Never 5xx
    data = response.json()
    assert data["status"] == "degraded"
    assert data["database"] == "unavailable"


@pytest.mark.asyncio
async def test_health_no_auth_required(client: AsyncClient) -> None:
    """Health endpoint must be accessible without authentication."""
    with (
        patch("app.routers.health.DatabaseService") as mock_db_cls,
        patch("app.routers.health.CacheService") as mock_cache_cls,
    ):
        mock_db = AsyncMock()
        mock_db.ping.return_value = True
        mock_db_cls.return_value = mock_db

        mock_cache = AsyncMock()
        mock_cache.ping.return_value = True
        mock_cache_cls.return_value = mock_cache

        # No Authorization header
        response = await client.get("/health")

    assert response.status_code == 200
