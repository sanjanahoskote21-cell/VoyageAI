# app/services/email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import get_settings

settings = get_settings()


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends a plain-text email via Gmail SMTP. Returns True if sent
    successfully, False otherwise (e.g. SMTP_USER/SMTP_PASSWORD not
    configured, or the send failed) — callers should not crash the
    request just because email delivery failed.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("[email] SMTP_USER/SMTP_PASSWORD not configured — skipping send")
        return False

    message = MIMEMultipart()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, message.as_string())
        return True
    except smtplib.SMTPException as exc:
        print(f"[email] Failed to send to {to_email}: {exc}")
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