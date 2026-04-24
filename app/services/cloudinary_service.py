"""Cloudinary integration for diagram and image uploads."""
from typing import Optional

import cloudinary
import cloudinary.uploader

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

ALLOWED_CONTENT_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/svg+xml": ".svg",
    "application/pdf": ".pdf",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def init_cloudinary() -> None:
    """Initialize Cloudinary SDK with credentials from settings."""
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


class CloudinaryService:
    """
    Service for uploading diagrams and images to Cloudinary.
    Uses signed uploads for security.
    Free tier: 25GB storage, 25GB bandwidth/month.
    """

    def __init__(self) -> None:
        init_cloudinary()

    async def upload_diagram(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        folder: str = "portfolio/diagrams",
    ) -> str:
        """
        Upload a file to Cloudinary and return the CDN URL.
        Validates file type and size before upload.
        Uses signed upload for security.
        """
        # Validate file type
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"File type '{content_type}' not allowed. "
                f"Allowed types: {', '.join(ALLOWED_CONTENT_TYPES.keys())}"
            )

        # Validate file size
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size {len(file_bytes)} bytes exceeds maximum of {MAX_FILE_SIZE_BYTES} bytes (10MB)"
            )

        # Determine resource type
        resource_type = "raw" if content_type == "application/pdf" else "image"

        try:
            result = cloudinary.uploader.upload(
                file_bytes,
                folder=folder,
                public_id=filename,
                resource_type=resource_type,
                use_filename=True,
                unique_filename=True,
                overwrite=False,
            )
            cdn_url: str = result["secure_url"]
            logger.info("cloudinary_upload_success", url=cdn_url, filename=filename)
            return cdn_url

        except Exception as exc:
            logger.error("cloudinary_upload_failed", filename=filename, error=str(exc))
            raise RuntimeError(f"Upload failed: {exc}") from exc

    def delete_file(self, public_id: str) -> bool:
        """Delete a file from Cloudinary by public ID."""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as exc:
            logger.error("cloudinary_delete_failed", public_id=public_id, error=str(exc))
            return False
