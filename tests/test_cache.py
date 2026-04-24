"""Tests for CacheService."""
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.cache import CacheService


@pytest.fixture
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.keys = AsyncMock(return_value=[])
    redis.ping = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def cache(mock_redis: AsyncMock) -> CacheService:
    return CacheService(mock_redis)


@pytest.mark.asyncio
async def test_cache_set_and_get(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache set stores value; get retrieves it."""
    mock_redis.get.return_value = json.dumps({"data": "value"})

    result = await cache.set("test_key", {"data": "value"}, ttl=60)
    assert result is True
    mock_redis.setex.assert_called_once()

    value = await cache.get("test_key")
    assert value is not None


@pytest.mark.asyncio
async def test_cache_miss_returns_none(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache miss returns None."""
    mock_redis.get.return_value = None
    result = await cache.get("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_delete(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache delete removes the key."""
    mock_redis.delete.return_value = 1
    result = await cache.delete("test_key")
    assert result is True


@pytest.mark.asyncio
async def test_cache_invalidate_pattern(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache invalidate_pattern deletes matching keys."""
    mock_redis.keys.return_value = ["projects:list:0:10:None", "projects:list:0:20:done"]
    mock_redis.delete.return_value = 2

    count = await cache.invalidate_pattern("projects:*")
    assert count == 2
    mock_redis.keys.assert_called_once_with("projects:*")


@pytest.mark.asyncio
async def test_cache_ping_success(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache ping returns True when Redis is reachable."""
    mock_redis.ping.return_value = True
    result = await cache.ping()
    assert result is True


@pytest.mark.asyncio
async def test_cache_ping_failure(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache ping returns False when Redis is unreachable."""
    mock_redis.ping.side_effect = Exception("Connection refused")
    result = await cache.ping()
    assert result is False


@pytest.mark.asyncio
async def test_cache_get_failure_returns_none(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache get failure returns None (degraded mode)."""
    mock_redis.get.side_effect = Exception("Redis unavailable")
    result = await cache.get("any_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_set_failure_returns_false(cache: CacheService, mock_redis: AsyncMock) -> None:
    """Cache set failure returns False (degraded mode)."""
    mock_redis.setex.side_effect = Exception("Redis unavailable")
    result = await cache.set("any_key", "value", ttl=60)
    assert result is False
