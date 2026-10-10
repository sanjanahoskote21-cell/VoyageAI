# backend/test/api/test_recommendations_api.py

import uuid

from app.models.trip import Trip, TripPlace
from app.services.place_service import get_or_create_place


def _make_trip(db, owner, with_place=True):
    trip = Trip(
        user_id=owner.id,
        start_location="Bengaluru",
        end_location="Mysore",
        num_days=2,
        num_travelers=2,
        budget_tier="mid",
        travel_mode="car",
    )
    db.add(trip)
    db.flush()

    if with_place:
        palace, _ = get_or_create_place(
            db, name="Mysore Palace", city="Mysore", category="palace",
            latitude=12.3052, longitude=76.6552, avg_rating=4.6,
        )
        db.add(TripPlace(trip_id=trip.id, place_id=palace.id, visit_order=1))
    db.commit()
    return trip


def _add_candidates(db):
    get_or_create_place(
        db, name="Brindavan Gardens", city="Mysore", category="garden",
        latitude=12.4244, longitude=76.5724, avg_rating=4.3,
    )
    get_or_create_place(
        db, name="Mysore Zoo", city="Mysore", category="zoo",
        latitude=12.3017, longitude=76.6527, avg_rating=4.4,
    )
    db.commit()


def _url(trip_id):
    return f"/api/v1/trips/{trip_id}/recommendations"


def test_owner_gets_recommendations_without_places_already_on_the_trip(client, db_session, user, auth_headers):
    trip = _make_trip(db_session, user)
    _add_candidates(db_session)

    resp = client.get(_url(trip.id), headers=auth_headers)

    assert resp.status_code == 200
    names = [r["name"] for r in resp.json()]
    assert "Brindavan Gardens" in names
    assert "Mysore Zoo" in names
    assert "Mysore Palace" not in names  # already on the trip


def test_recommendations_are_sorted_best_first_and_scores_are_sane(client, db_session, user, auth_headers):
    trip = _make_trip(db_session, user)
    _add_candidates(db_session)

    results = client.get(_url(trip.id), headers=auth_headers).json()

    scores = [r["final_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    for r in results:
        assert 0.0 <= r["final_score"] <= 1.0
        assert 0.0 <= r["proximity_score"] <= 1.0


def test_trip_with_no_places_returns_an_empty_list(client, db_session, user, auth_headers):
    trip = _make_trip(db_session, user, with_place=False)
    _add_candidates(db_session)

    resp = client.get(_url(trip.id), headers=auth_headers)

    assert resp.status_code == 200
    assert resp.json() == []


def test_recommendations_for_another_users_trip_return_404(client, db_session, other_user, auth_headers):
    theirs = _make_trip(db_session, other_user)
    _add_candidates(db_session)

    resp = client.get(_url(theirs.id), headers=auth_headers)

    assert resp.status_code == 404
    assert "Brindavan" not in resp.text


def test_recommendations_for_a_nonexistent_trip_return_404(client, auth_headers):
    assert client.get(_url(uuid.uuid4()), headers=auth_headers).status_code == 404


def test_recommendations_without_a_token_are_rejected(client, db_session, user):
    trip = _make_trip(db_session, user)
    # Older FastAPI returns 403 here, newer versions 401. Both mean "rejected".
    assert client.get(_url(trip.id)).status_code in (401, 403)