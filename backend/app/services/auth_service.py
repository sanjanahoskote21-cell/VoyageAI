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
)
from app.core.config import get_settings

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
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, credentials: UserLogin) -> str:
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    return create_access_token(user_id=str(user.id))


def request_password_reset(db: Session, email: str) -> str | None:
    """
    Always looks and behaves the same whether or not the email exists —
    prevents attackers from using this endpoint to discover which emails
    are registered.

    Returns the reset link ONLY when ENVIRONMENT=development, so it can be
    tested without a real email service. In any other environment this
    always returns None — the link is only ever logged server-side, never
    handed back to the client.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    token = create_password_reset_token(str(user.id))
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    # TODO: replace with a real email service (SendGrid/SMTP) later.
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