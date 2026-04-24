"""Contact form endpoints."""
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.core.database import get_db
from app.core.email import get_email_service
from app.core.logging import get_logger
from app.models.contact_message import ContactMessage
from app.schemas.contact import (
    ContactMessageCreate,
    ContactMessageResponse,
    ContactMessageUpdate,
)
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["contact"])
logger = get_logger(__name__)


@router.post("/contact", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact_form(
    contact_data: ContactMessageCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
) -> ContactMessageResponse:
    """
    Submit contact form (public endpoint).
    Sends email notification to admin.
    """
    db = DatabaseService(session)

    # Create contact message
    contact = ContactMessage(**contact_data.model_dump())
    created = await db.create(contact)

    # Send email notification in background
    background_tasks.add_task(
        _send_contact_notification,
        name=created.name,
        email=created.email,
        subject=created.subject,
        message=created.message,
        contact_id=created.id,
    )

    logger.info(
        "contact_form_submitted",
        contact_id=created.id,
        email=created.email,
        subject=created.subject,
    )

    return ContactMessageResponse.model_validate(created)


@router.get("/admin/contact", response_model=List[ContactMessageResponse])
async def list_contact_messages(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    unread_only: bool = Query(default=False),
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> List[ContactMessageResponse]:
    """List contact messages (admin only). Ordered by newest first."""
    db = DatabaseService(session)

    filters = {"is_read": False} if unread_only else None
    messages = await db.get_all(
        ContactMessage,
        skip=skip,
        limit=limit,
        filters=filters,
        order_by=[desc(ContactMessage.created_at)],
    )

    return [ContactMessageResponse.model_validate(m) for m in messages]


@router.get("/admin/contact/{message_id}", response_model=ContactMessageResponse)
async def get_contact_message(
    message_id: int,
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> ContactMessageResponse:
    """Get a single contact message (admin only)."""
    db = DatabaseService(session)
    message = await db.get_by_id(ContactMessage, message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found",
        )

    return ContactMessageResponse.model_validate(message)


@router.put("/admin/contact/{message_id}", response_model=ContactMessageResponse)
async def update_contact_message(
    message_id: int,
    update_data: ContactMessageUpdate,
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> ContactMessageResponse:
    """Update contact message status/notes (admin only)."""
    db = DatabaseService(session)
    message = await db.get_by_id(ContactMessage, message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    updated = await db.update(message, update_dict)

    logger.info("contact_message_updated", message_id=message_id)
    return ContactMessageResponse.model_validate(updated)


@router.delete("/admin/contact/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_message(
    message_id: int,
    session: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> None:
    """Delete contact message (admin only)."""
    db = DatabaseService(session)
    message = await db.get_by_id(ContactMessage, message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found",
        )

    await db.delete(message)
    logger.info("contact_message_deleted", message_id=message_id)


def _send_contact_notification(
    name: str, email: str, subject: str, message: str, contact_id: int
) -> None:
    """Background task to send email notification."""
    email_service = get_email_service()
    email_service.send_contact_notification(
        name=name,
        email=email,
        subject=subject,
        message=message,
        contact_id=contact_id,
    )
