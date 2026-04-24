"""CacheService — Upstash Redis abstraction with command-budget awareness."""
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """
    Redis cache service optimized for Upstash free tier (10k commands/day).
    All operations are wrapped in try/except for graceful degradation.
    Uses SETEX (1 command) instead of SET + EXPIRE (2 commands).
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from cache. Returns None on miss or error.
        Cost: 1 Redis command.
        """
        try:
            return await self.redis.get(key)
        except Exception as exc:
            logger.warning("cache_get_failed", key=key, error=str(exc))
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set a value in cache with TTL using SETEX (1 command).
        Value is JSON-serialized if not already a string.
        Cost: 1 Redis command.
        """
        try:
            serialized = value if isinstance(value, str) else json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as exc:
            logger.warning("cache_set_failed", key=key, error=str(exc))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        Cost: 1 Redis command.
        """
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as exc:
            logger.warning("cache_delete_failed", key=key, error=str(exc))
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a glob pattern.
        Uses KEYS + DEL — use sparingly in hot paths (costs 2+ commands).
        Cost: 1 (KEYS) + 1 (DEL) Redis commands minimum.
        """
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info("cache_invalidated", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as exc:
            logger.warning("cache_invalidate_failed", pattern=pattern, error=str(exc))
            return 0

    async def ping(self) -> bool:
        """Check Redis connectivity. Returns True if reachable."""
        try:
            await self.redis.ping()
            return True
        except Exception as exc:
            logger.warning("cache_ping_failed", error=str(exc))
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize a JSON value from cache."""
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
