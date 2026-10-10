# backend/test/api/test_auth_api.py

from app.core.security import create_email_verification_token
from app.models.user import User

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"
VERIFY = "/api/v1/auth/verify-email"

PASSWORD = "CorrectHorse9!"


def _payload(**overrides):
    data = {"email": "asha@example.com", "password": PASSWORD, "full_name": "Asha Rao"}
    data.update(overrides)
    return data


# -- register ----------------------------------------------------------

def test_register_creates_unverified_user_and_sends_verification_email(client, mock_email):
    resp = client.post(REGISTER, json=_payload())

    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "asha@example.com"
    assert body["is_verified"] is False
    assert mock_email.verification.call_count == 1
    assert mock_email.verification.call_args.args[0] == "asha@example.com"


def test_register_response_never_contains_password_fields(client):
    body = client.post(REGISTER, json=_payload()).json()
    assert not any("password" in key for key in body)


def test_register_stores_a_hash_not_the_plain_password(client, db_session):
    client.post(REGISTER, json=_payload())

    saved = db_session.query(User).filter(User.email == "asha@example.com").one()
    assert saved.password_hash != PASSWORD
    assert len(saved.password_hash) > 20


def test_register_duplicate_email_is_rejected(client, db_session, make_user):
    make_user(email="asha@example.com")

    resp = client.post(REGISTER, json=_payload())

    assert resp.status_code == 400
    assert db_session.query(User).filter(User.email == "asha@example.com").count() == 1


def test_register_invalid_email_is_rejected(client):
    resp = client.post(REGISTER, json=_payload(email="not-an-email"))
    assert resp.status_code == 422


# -- login -------------------------------------------------------------

def test_login_success_returns_a_token_that_works(client, make_user):
    user = make_user(password=PASSWORD)

    resp = client.post(LOGIN, json={"email": user.email, "password": PASSWORD})

    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"

    me = client.get(ME, headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == user.email


def test_login_wrong_password_fails(client, make_user):
    user = make_user(password=PASSWORD)
    resp = client.post(LOGIN, json={"email": user.email, "password": "wrong-password"})
    assert resp.status_code == 401


def test_login_unknown_email_gives_the_same_error_as_wrong_password(client, make_user):
    user = make_user(password=PASSWORD)
    wrong_password = client.post(LOGIN, json={"email": user.email, "password": "nope"})
    unknown_email = client.post(LOGIN, json={"email": "nobody@example.com", "password": "nope"})

    assert unknown_email.status_code == wrong_password.status_code == 401
    assert unknown_email.json()["detail"] == wrong_password.json()["detail"]


def test_login_is_blocked_until_the_email_is_verified(client, make_user):
    user = make_user(password=PASSWORD, is_verified=False)
    resp = client.post(LOGIN, json={"email": user.email, "password": PASSWORD})
    assert resp.status_code == 403


# -- /auth/me ----------------------------------------------------------

def test_me_returns_the_current_user(client, user, auth_headers):
    resp = client.get(ME, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == user.email


def test_me_without_a_token_is_rejected(client):
    # Older FastAPI returns 403 here, newer versions 401. Both mean "rejected".
    assert client.get(ME).status_code in (401, 403)


def test_me_with_a_garbage_token_is_rejected(client):
    resp = client.get(ME, headers={"Authorization": "Bearer not.a.real.token"})
    assert resp.status_code == 401


# -- email verification ------------------------------------------------

def test_verify_email_flow_unlocks_login(client, db_session):
    client.post(REGISTER, json=_payload())
    new_user = db_session.query(User).filter(User.email == "asha@example.com").one()
    assert new_user.is_verified is False

    token = create_email_verification_token(str(new_user.id))
    verify = client.post(VERIFY, json={"token": token})
    assert verify.status_code == 204

    db_session.refresh(new_user)
    assert new_user.is_verified is True

    login = client.post(LOGIN, json={"email": "asha@example.com", "password": PASSWORD})
    assert login.status_code == 200


def test_verify_email_with_an_invalid_token_is_rejected(client):
    resp = client.post(VERIFY, json={"token": "garbage"})
    assert resp.status_code == 400