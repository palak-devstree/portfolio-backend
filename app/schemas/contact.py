"""Pydantic schemas for contact messages."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ContactMessageCreate(BaseModel):
    """Schema for creating a contact message."""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=500)
    message: str = Field(..., min_length=10, max_length=5000)


class ContactMessageUpdate(BaseModel):
    """Schema for updating contact message (admin only)."""

    is_read: Optional[bool] = None
    is_replied: Optional[bool] = None
    admin_notes: Optional[str] = Field(None, max_length=5000)


class ContactMessageResponse(BaseModel):
    """Schema for contact message responses."""

    id: int
    name: str
    email: str
    subject: str
    message: str
    is_read: bool
    is_replied: bool
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
