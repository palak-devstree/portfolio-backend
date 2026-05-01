"""File upload endpoint for Cloudinary image storage."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from app.core.auth import get_current_admin
from app.core.logging import get_logger
from app.services.cloudinary_service import CloudinaryService

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])
logger = get_logger(__name__)

ImageType = Literal["diagram", "certificate", "education", "experience", "profile"]


@router.post("/image")
async def upload_image(
    file: UploadFile,
    image_type: ImageType = Query(..., description="Type of image being uploaded"),
    _: dict = Depends(get_current_admin),
) -> dict:
    """
    Upload an image to Cloudinary.
    Admin only. Allowed types: PNG, JPG, JPEG, SVG, PDF. Max size: 10MB.
    Returns the Cloudinary CDN URL.
    
    Image types:
    - diagram: System design diagrams
    - certificate: Certificate images
    - education: Education-related images
    - experience: Experience/work-related images
    - profile: Profile pictures
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    content_type = file.content_type or "application/octet-stream"
    file_bytes = await file.read()

    # Map image type to folder
    folder_map = {
        "diagram": "portfolio/diagrams",
        "certificate": "portfolio/certificates",
        "education": "portfolio/education",
        "experience": "portfolio/experience",
        "profile": "portfolio/profile",
    }

    service = CloudinaryService()
    try:
        cdn_url = await service.upload_image(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=content_type,
            folder=folder_map[image_type],
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

    logger.info("image_uploaded", filename=file.filename, url=cdn_url, type=image_type)
    return {"url": cdn_url, "filename": file.filename}


# Legacy endpoint for backward compatibility
@router.post("/diagram")
async def upload_diagram(
    file: UploadFile,
    _: dict = Depends(get_current_admin),
) -> dict:
    """
    Upload a diagram to Cloudinary (legacy endpoint).
    Use /image?image_type=diagram instead.
    """
    return await upload_image(file, image_type="diagram", _=_)
