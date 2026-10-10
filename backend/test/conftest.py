# backend/tests/conftest.py
"""
Shared test fixtures.

- Tests run on a throwaway Postgres database (TEST_DATABASE_URL), never on
  Supabase. A safety check refuses to run against anything that isn't
  clearly a test database.
- Each test runs inside a transaction that is rolled back at the end, so
  tests never see each other's data and the DB is always clean.
- Rate limiting is switched off so tests can hit endpoints repeatedly.
- Tests that don't use db_session (like the route optimizer tests) still
  run without any database configured.
"""
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _load_env_test() -> None:
    """Tiny .env.test reader so you don't have to export variables by hand."""
    path = BACKEND_DIR / ".env.test"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_test()


@pytest.fixture(autouse=True)
def _disable_rate_limits():
    from app.core.limiter import limiter

    limiter.enabled = False
    yield


@pytest.fixture(scope="session")
def engine():
    from app.core.config import get_settings
    from app.db.base import Base

    # Importing every model registers all tables on Base.metadata.
    from app.models import (  # noqa: F401
        budget,
        chat_message,
        hotel,
        place,
        restaurant,
        trip,
        user,
    )

    test_url = os.environ.get("TEST_DATABASE_URL")
    if not test_url:
        pytest.exit("TEST_DATABASE_URL is not set. Add it to backend/.env.test", returncode=2)

    parsed = make_url(test_url)
    if (
        test_url == get_settings().DATABASE_URL
        or "supabase" in (parsed.host or "")
        or "test" not in (parsed.database or "").lower()
    ):
        pytest.exit(
            "Refusing to run: TEST_DATABASE_URL must be a separate database whose "
            "name contains 'test', and must not be Supabase.",
            returncode=2,
        )

    eng = create_engine(test_url)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db_session(engine):
    """A session whose work is rolled back after every test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        autoflush=False,
        join_transaction_mode="create_savepoint",  # app code can commit() safely
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI test client wired to the rolled-back test session."""
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()