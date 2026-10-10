# backend/test/api/conftest.py
"""
Fixtures shared by the API tests.

- Email sending is patched for every test, so nothing ever touches SMTP, and
  tests can assert that an email was (or wasn't) sent.
- make_user inserts a user straight into the rolled-back test database, with
  a real password hash and is_verified=True unless told otherwise.
"""
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.security import create_access_token, hash_password
from app.models.user import User


@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    verification = MagicMock(return_value=True)
    reset = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.auth_service.send_verification_email", verification)
    monkeypatch.setattr("app.services.auth_service.send_password_reset_email", reset)
    return SimpleNamespace(verification=verification, reset=reset)


@pytest.fixture
def make_user(db_session):
    def _make(email=None, full_name="Test User", password="CorrectHorse9!", is_verified=True):
        user = User(
            email=email or f"user-{uuid.uuid4().hex[:8]}@example.com",
            password_hash=hash_password(password),
            full_name=full_name,
            is_verified=is_verified,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make


@pytest.fixture
def auth_headers_for():
    def _headers(user):
        return {"Authorization": f"Bearer {create_access_token(user_id=str(user.id))}"}

    return _headers


@pytest.fixture
def user(make_user):
    return make_user(full_name="Asha Rao")


@pytest.fixture
def auth_headers(user, auth_headers_for):
    return auth_headers_for(user)


@pytest.fixture
def other_user(make_user):
    return make_user(full_name="Someone Else")