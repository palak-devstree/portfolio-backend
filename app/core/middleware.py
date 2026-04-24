"""FastAPI middleware: CORS, security headers, request logging, rate limiting."""
import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with structured logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        # Bind request context for all log calls in this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Token bucket rate limiting using Redis.
    - Anonymous: 100 req/min
    - Authenticated: 1000 req/min
    Degrades gracefully if Redis is unavailable.
    """

    ANONYMOUS_LIMIT = 100
    AUTHENTICATED_LIMIT = 1000
    WINDOW_SECONDS = 60

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        try:
            from app.core.cache import get_redis_client
            redis = get_redis_client()

            # Determine if authenticated
            auth_header = request.headers.get("Authorization", "")
            is_authenticated = auth_header.startswith("Bearer ")
            limit = self.AUTHENTICATED_LIMIT if is_authenticated else self.ANONYMOUS_LIMIT

            # Use IP as rate limit key
            client_ip = request.client.host if request.client else "unknown"
            key = f"rate_limit:{client_ip}:{'auth' if is_authenticated else 'anon'}"

            # Increment counter with TTL
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self.WINDOW_SECONDS)

            if count > limit:
                logger.warning(
                    "rate_limit_exceeded",
                    client_ip=client_ip,
                    count=count,
                    limit=limit,
                )
                return Response(
                    content='{"detail": "Rate limit exceeded. Try again later."}',
                    status_code=429,
                    media_type="application/json",
                    headers={"Retry-After": str(self.WINDOW_SECONDS)},
                )

        except Exception as exc:
            # Degrade gracefully — don't block requests if Redis is down
            logger.warning("rate_limit_redis_unavailable", error=str(exc))

        return await call_next(request)


def setup_middleware(app) -> None:
    """Register all middleware on the FastAPI app."""
    # CORS must be added first (outermost layer)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=86400,  # 24 hours preflight cache
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Rate limiting
    app.add_middleware(RateLimitMiddleware)
