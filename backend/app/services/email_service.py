# app/services/email_service.py

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"
EMAIL_TIMEOUT_SECONDS = 10  # never let an email provider hold a request for minutes


def _send_via_brevo(to_email: str, subject: str, body: str) -> bool:
    """HTTPS call to Brevo. Works on hosts that block SMTP ports (Render free tier)."""
    sender_email = settings.EMAIL_FROM or settings.SMTP_USER
    if not sender_email:
        logger.error("[email] BREVO_API_KEY is set but no sender (EMAIL_FROM / SMTP_USER)")
        return False

    try:
        response = httpx.post(
            BREVO_SEND_URL,
            headers={
                "api-key": settings.BREVO_API_KEY,
                "accept": "application/json",
                "content-type": "application/json",
            },
            json={
                "sender": {"name": "VoyageAI", "email": sender_email},
                "to": [{"email": to_email}],
                "subject": subject,
                "textContent": body,
            },
            timeout=EMAIL_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:  # timeouts, connection errors
        logger.error("[email] Brevo request failed for %s: %s", to_email, exc)
        return False

    if response.status_code in (200, 201):
        return True

    logger.error("[email] Brevo rejected email to %s: %s %s", to_email, response.status_code, response.text)
    return False


def _send_via_smtp(to_email: str, subject: str, body: str) -> bool:
    """Gmail SMTP. Fine locally; blocked on Render's free tier."""
    message = MIMEMultipart()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=EMAIL_TIMEOUT_SECONDS) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, message.as_string())
        return True
    except (smtplib.SMTPException, OSError) as exc:  # OSError covers timeouts / blocked ports
        logger.error("[email] SMTP send to %s failed: %s", to_email, exc)
        return False


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends a plain-text email. Returns True if sent, False otherwise, so callers
    never crash a request just because email delivery failed.

    Uses Brevo's HTTP API when BREVO_API_KEY is set (needed on Render's free tier),
    otherwise falls back to Gmail SMTP, otherwise skips.
    """
    if settings.BREVO_API_KEY:
        return _send_via_brevo(to_email, subject, body)

    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        return _send_via_smtp(to_email, subject, body)

    logger.warning("[email] No email provider configured - skipping send")
    return False


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    subject = "Reset your VoyageAI password"
    body = (
        f"Hi,\n\n"
        f"We received a request to reset your VoyageAI password. "
        f"Click the link below to set a new one — it expires in 15 minutes:\n\n"
        f"{reset_link}\n\n"
        f"If you didn't request this, you can safely ignore this email.\n\n"
        f"— VoyageAI"
    )
    return send_email(to_email, subject, body)


def send_verification_email(to_email: str, verify_link: str) -> bool:
    subject = "Verify your VoyageAI email"
    body = (
        f"Hi,\n\n"
        f"Thanks for signing up for VoyageAI! Please verify your email to "
        f"activate your account — this link expires in 24 hours:\n\n"
        f"{verify_link}\n\n"
        f"If you didn't create this account, you can safely ignore this email.\n\n"
        f"— VoyageAI"
    )
    return send_email(to_email, subject, body)