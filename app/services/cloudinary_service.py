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
    "image/jpg": ".jpg",
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

    async def upload_image(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        folder: str = "portfolio/images",
    ) -> str:
        """
        Upload an image file to Cloudinary and return the CDN URL.
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
            logger.info(
                "cloudinary_upload_success",
                url=cdn_url,
                filename=filename,
                public_id=result.get("public_id"),
                full_result=result,
            )
            return cdn_url

        except Exception as exc:
            logger.error("cloudinary_upload_failed", filename=filename, error=str(exc))
            raise RuntimeError(f"Upload failed: {exc}") from exc

    # Legacy method name for backward compatibility
    async def upload_diagram(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        folder: str = "portfolio/diagrams",
    ) -> str:
        """Legacy method. Use upload_image instead."""
        return await self.upload_image(file_bytes, filename, content_type, folder)

    def delete_file(self, public_id: str) -> bool:
        """Delete a file from Cloudinary by public ID."""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as exc:
            logger.error("cloudinary_delete_failed", public_id=public_id, error=str(exc))
            return False

    def delete_by_url(self, url: str) -> bool:
        """
        Delete a file from Cloudinary by extracting public_id from URL.
        Handles both image and raw resource types.
        """
        try:
            public_id = self._extract_public_id_from_url(url)
            if not public_id:
                logger.warning("cloudinary_delete_invalid_url", url=url)
                return False

            # Try deleting as image first
            result = cloudinary.uploader.destroy(public_id, resource_type="image")
            if result.get("result") == "ok":
                logger.info("cloudinary_delete_success", public_id=public_id, type="image")
                return True

            # If not found as image, try as raw (for PDFs)
            result = cloudinary.uploader.destroy(public_id, resource_type="raw")
            if result.get("result") == "ok":
                logger.info("cloudinary_delete_success", public_id=public_id, type="raw")
                return True

            logger.warning("cloudinary_delete_not_found", public_id=public_id)
            return False

        except Exception as exc:
            logger.error("cloudinary_delete_by_url_failed", url=url, error=str(exc))
            return False

    def _extract_public_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract public_id from Cloudinary URL.
        Example: https://res.cloudinary.com/cloud/image/upload/v123/folder/file.png
        Returns: folder/file
        """
        if not url or "cloudinary.com" not in url:
            return None

        try:
            # Split by /upload/ to get the part after it
            parts = url.split("/upload/")
            if len(parts) < 2:
                return None

            # Get everything after /upload/
            after_upload = parts[1]

            # Remove version (v1234567890) if present
            if after_upload.startswith("v"):
                after_upload = "/".join(after_upload.split("/")[1:])

            # Remove file extension
            public_id = after_upload.rsplit(".", 1)[0]

            return public_id
        except Exception as exc:
            logger.error("extract_public_id_failed", url=url, error=str(exc))
            return None
