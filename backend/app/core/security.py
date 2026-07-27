# app/core/security.py

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_RESET_EXPIRE_MINUTES = 15
EMAIL_VERIFICATION_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """
    Returns the user_id encoded in the token, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def create_password_reset_token(user_id: str) -> str:
    """
    Short-lived token (15 min) scoped only for password resets — it carries
    a 'scope' claim so it can never be accepted by the normal auth dependency
    even though it's signed with the same secret.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire, "scope": "password_reset"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_password_reset_token(token: str) -> str | None:
    """
    Returns the user_id if the token is valid, unexpired, and scoped for
    password resets. Returns None otherwise (invalid, expired, or a
    regular access token being reused here).
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("scope") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_email_verification_token(user_id: str) -> str:
    """
    24-hour token scoped only for email verification — same pattern as
    the password reset token, different scope claim so the two can never
    be swapped for one another.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=EMAIL_VERIFICATION_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire, "scope": "email_verification"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_email_verification_token(token: str) -> str | None:
    """
    Returns the user_id if the token is valid, unexpired, and scoped for
    email verification. Returns None otherwise.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("scope") != "email_verification":
            return None
        return payload.get("sub")
    except JWTError:
        return None