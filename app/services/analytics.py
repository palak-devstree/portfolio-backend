"""Analytics tracking service with IP anonymization."""
import ipaddress
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.analytics import Analytics
from app.services.database import DatabaseService

logger = get_logger(__name__)


def anonymize_ip(ip: str) -> str:
    """
    Anonymize IP address for GDPR compliance.
    - IPv4: mask last octet (e.g., 192.168.1.100 → 192.168.1.0)
    - IPv6: mask last 80 bits (keep first 48 bits)
    """
    try:
        addr = ipaddress.ip_address(ip)
        if isinstance(addr, ipaddress.IPv4Address):
            # Mask last octet
            parts = ip.split(".")
            parts[-1] = "0"
            return ".".join(parts)
        else:
            # IPv6: keep first 48 bits (3 groups), zero the rest
            packed = addr.packed
            anonymized = packed[:6] + b"\x00" * 10
            return str(ipaddress.IPv6Address(anonymized))
    except ValueError:
        return "0.0.0.0"


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP from request, checking forwarded headers."""
    # Check X-Forwarded-For (set by Render/Railway reverse proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    # Fall back to direct connection IP
    if request.client:
        return request.client.host
    return None


async def track_event(
    session: AsyncSession,
    event_type: str,
    request: Request,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> None:
    """
    Track an analytics event asynchronously.
    IP addresses are anonymized before storage.
    Errors are logged but do not propagate (fire-and-forget).
    """
    try:
        raw_ip = get_client_ip(request)
        anon_ip = anonymize_ip(raw_ip) if raw_ip else None

        event = Analytics(
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            user_agent=request.headers.get("User-Agent", "")[:500],
            ip_address=anon_ip,
            event_metadata=metadata,  # Renamed from 'metadata'
        )

        db = DatabaseService(session)
        await db.create(event)

    except Exception as exc:
        # Analytics failures must never break the main request
        logger.warning("analytics_track_failed", event_type=event_type, error=str(exc))
