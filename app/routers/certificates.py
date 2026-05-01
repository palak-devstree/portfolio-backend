"""Certificates REST API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateResponse, CertificateUpdate
from app.services.cache import CacheService
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/certificates", tags=["certificates"])
logger = get_logger(__name__)

CACHE_TTL = 300  # 5 minutes


@router.get("", response_model=List[CertificateResponse])
async def list_certificates(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> List[CertificateResponse]:
    """
    List certificates with pagination.
    Results ordered by display_order ASC, then created_at DESC.
    Cached for 5 minutes.
    """
    cache_key = f"certificates:list:{skip}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        import json
        return [CertificateResponse(**c) for c in json.loads(cached)]

    db = DatabaseService(session)
    certificates = await db.get_all(
        Certificate,
        skip=skip,
        limit=limit,
        order_by=[asc(Certificate.display_order), desc(Certificate.created_at)],
    )

    response = [CertificateResponse.model_validate(c) for c in certificates]
    await cache.set(cache_key, [r.model_dump(mode="json") for r in response], ttl=CACHE_TTL)
    return response


@router.get("/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(
    certificate_id: int,
    session: AsyncSession = Depends(get_db),
) -> CertificateResponse:
    """Get a single certificate by ID."""
    db = DatabaseService(session)
    certificate = await db.get_by_id(Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    return CertificateResponse.model_validate(certificate)


@router.post("", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
async def create_certificate(
    certificate_data: CertificateCreate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> CertificateResponse:
    """Create a new certificate. Admin only."""
    db = DatabaseService(session)
    certificate = Certificate(**certificate_data.model_dump())
    created = await db.create(certificate)
    await cache.invalidate_pattern("certificates:*")
    logger.info("certificate_created", certificate_id=created.id, title=created.title)
    return CertificateResponse.model_validate(created)


@router.put("/{certificate_id}", response_model=CertificateResponse)
async def update_certificate(
    certificate_id: int,
    certificate_data: CertificateUpdate,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> CertificateResponse:
    """Update an existing certificate. Admin only."""
    db = DatabaseService(session)
    certificate = await db.get_by_id(Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")

    update_data = certificate_data.model_dump(exclude_unset=True)
    updated = await db.update(certificate, update_data)
    await cache.invalidate_pattern("certificates:*")
    logger.info("certificate_updated", certificate_id=certificate_id)
    return CertificateResponse.model_validate(updated)


@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certificate(
    certificate_id: int,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete a certificate and its associated Cloudinary image. Admin only."""
    db = DatabaseService(session)
    certificate = await db.get_by_id(Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")

    # Delete from Cloudinary if image_url exists
    if certificate.image_url:
        try:
            from app.services.cloudinary_service import CloudinaryService
            cloudinary_service = CloudinaryService()
            deleted = cloudinary_service.delete_by_url(certificate.image_url)
            if deleted:
                logger.info("cloudinary_image_deleted", certificate_id=certificate_id, url=certificate.image_url)
            else:
                logger.warning("cloudinary_image_not_deleted", certificate_id=certificate_id, url=certificate.image_url)
        except Exception as exc:
            logger.error("cloudinary_cleanup_failed", certificate_id=certificate_id, error=str(exc))

    await db.delete(certificate)
    await cache.invalidate_pattern("certificates:*")
    logger.info("certificate_deleted", certificate_id=certificate_id)

