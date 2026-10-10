# backend/test/api/test_profile_api.py

ME = "/api/v1/auth/me"


def test_patch_me_updates_the_name(client, db_session, user, auth_headers):
    resp = client.patch(ME, json={"full_name": "Asha R. Rao"}, headers=auth_headers)

    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Asha R. Rao"
    db_session.refresh(user)
    assert user.full_name == "Asha R. Rao"


def test_patch_me_trims_whitespace_from_the_name(client, auth_headers):
    resp = client.patch(ME, json={"full_name": "   Asha   "}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Asha"


def test_patch_me_rejects_a_blank_name(client, db_session, user, auth_headers):
    resp = client.patch(ME, json={"full_name": "   "}, headers=auth_headers)

    assert resp.status_code == 400
    db_session.refresh(user)
    assert user.full_name == "Asha Rao"  # unchanged


def test_patch_me_without_the_name_field_is_rejected(client, auth_headers):
    resp = client.patch(ME, json={}, headers=auth_headers)
    assert resp.status_code == 422


def test_patch_me_without_a_token_is_rejected(client):
    # Older FastAPI returns 403 here, newer versions 401. Both mean "rejected".
    resp = client.patch(ME, json={"full_name": "Hacker"})
    assert resp.status_code in (401, 403)


def test_patch_me_response_never_exposes_a_password_hash(client, auth_headers):
    body = client.patch(ME, json={"full_name": "Asha"}, headers=auth_headers).json()
    assert not any("password" in key for key in body)


def test_patch_me_cannot_change_the_email(client, user, auth_headers):
    original_email = user.email
    resp = client.patch(
        ME,
        json={"full_name": "Asha", "email": "hacker@example.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == original_email