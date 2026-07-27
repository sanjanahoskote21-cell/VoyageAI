# app/services/auth_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    create_email_verification_token,
    decode_email_verification_token,
)
from app.core.config import get_settings
from app.services.email_service import send_password_reset_email, send_verification_email

settings = get_settings()


def register_user(db: Session, user_data: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_email_verification_token(str(new_user.id))
    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    email_sent = send_verification_email(new_user.email, verify_link)
    if not email_sent:
        print(f"[email verification] link for {new_user.email}: {verify_link}")

    return new_user


def authenticate_user(db: Session, credentials: UserLogin) -> str:
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )

    return create_access_token(user_id=str(user.id))


def verify_email(db: Session, token: str) -> None:
    user_id = decode_email_verification_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link is invalid or has expired.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link is invalid or has expired.",
        )

    user.is_verified = True
    db.commit()


def resend_verification_email(db: Session, email: str) -> str | None:
    """
    Same non-leaking pattern as password reset: behaves identically
    whether or not the email exists or is already verified.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or user.is_verified:
        return None

    token = create_email_verification_token(str(user.id))
    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    email_sent = send_verification_email(email, verify_link)
    if not email_sent:
        print(f"[email verification] link for {email}: {verify_link}")
        if settings.ENVIRONMENT == "development":
            return verify_link

    return None


def request_password_reset(db: Session, email: str) -> str | None:
    """
    Always looks and behaves the same whether or not the email exists —
    prevents attackers from using this endpoint to discover which emails
    are registered.

    Tries to send the reset link by real email first. Returns the link
    back to the caller ONLY when:
      - ENVIRONMENT=development, AND
      - the email send failed or SMTP isn't configured
    so local testing still works without SMTP set up. In any other case
    (production, or the email sent successfully) this returns None — the
    link is never handed back to the client once it's actually emailed.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    token = create_password_reset_token(str(user.id))
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    email_sent = send_password_reset_email(email, reset_link)

    if not email_sent:
        print(f"[password reset] link for {email}: {reset_link}")
        if settings.ENVIRONMENT == "development":
            return reset_link

    return None


def reset_password(db: Session, token: str, new_password: str) -> None:
    user_id = decode_password_reset_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link is invalid or has expired.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link is invalid or has expired.",
        )

    user.password_hash = hash_password(new_password)
    db.commit()