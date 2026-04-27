"""Certificate Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CertificateBase(BaseModel):
    """Base certificate schema with common fields."""

    title: str = Field(..., min_length=1, max_length=255)
    issuer: str = Field(..., min_length=1, max_length=255)
    issue_date: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[str] = Field(None, max_length=50)
    credential_id: Optional[str] = Field(None, max_length=255)
    credential_url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    display_order: int = Field(default=0, ge=0)


class CertificateCreate(CertificateBase):
    """Schema for creating certificate."""
    pass


class CertificateUpdate(BaseModel):
    """Schema for updating certificate (all fields optional)."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    issuer: Optional[str] = Field(None, min_length=1, max_length=255)
    issue_date: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[str] = Field(None, max_length=50)
    credential_id: Optional[str] = Field(None, max_length=255)
    credential_url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)


class CertificateResponse(CertificateBase):
    """Schema for certificate responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
