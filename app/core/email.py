"""Email service using SMTP."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """SMTP email service for sending notifications."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> MIMEMultipart:
        """Create email message with HTML and optional text fallback."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        # Add text version if provided
        if text_body:
            msg.attach(MIMEText(text_body, "plain"))

        # Add HTML version
        msg.attach(MIMEText(html_body, "html"))

        return msg

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Send email via SMTP.
        Returns True if successful, False otherwise.
        """
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
            logger.warning("email_not_configured", message="SMTP settings missing")
            return False

        try:
            msg = self._create_message(to_email, subject, html_body, text_body)

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("email_sent", to=to_email, subject=subject)
            return True

        except Exception as exc:
            logger.error("email_send_failed", to=to_email, error=str(exc))
            return False

    def send_contact_notification(
        self,
        name: str,
        email: str,
        subject: str,
        message: str,
        contact_id: int,
    ) -> bool:
        """Send notification email when contact form is submitted."""
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #2563eb;">New Contact Form Submission</h2>
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Contact ID:</strong> #{contact_id}</p>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                    <p><strong>Subject:</strong> {subject}</p>
                </div>
                <div style="margin: 20px 0;">
                    <h3 style="color: #1f2937;">Message:</h3>
                    <p style="white-space: pre-wrap; background: #fff; padding: 15px; border-left: 4px solid #2563eb;">
{message}
                    </p>
                </div>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="color: #6b7280; font-size: 14px;">
                    This is an automated notification from your portfolio contact form.
                </p>
            </body>
        </html>
        """

        text_body = f"""
New Contact Form Submission

Contact ID: #{contact_id}
Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This is an automated notification from your portfolio contact form.
        """

        return self.send_email(
            to_email=settings.ADMIN_EMAIL,
            subject=f"New Contact: {subject}",
            html_body=html_body,
            text_body=text_body,
        )


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
