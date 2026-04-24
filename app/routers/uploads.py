"""File upload endpoint for Cloudinary diagram storage."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.auth import get_current_admin
from app.core.logging import get_logger
from app.services.cloudinary_service import CloudinaryService

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])
logger = get_logger(__name__)


@router.post("/diagram")
async def upload_diagram(
    file: UploadFile,
    _: dict = Depends(get_current_admin),
) -> dict:
    """
    Upload a diagram or image to Cloudinary.
    Admin only. Allowed types: PNG, JPG, SVG, PDF. Max size: 10MB.
    Returns the Cloudinary CDN URL.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    content_type = file.content_type or "application/octet-stream"
    file_bytes = await file.read()

    service = CloudinaryService()
    try:
        cdn_url = await service.upload_diagram(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=content_type,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upload service error: {exc}",
        )

    logger.info("diagram_uploaded", filename=file.filename, url=cdn_url)
    return {"url": cdn_url, "filename": file.filename}
