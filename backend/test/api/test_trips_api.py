# backend/test/api/test_trips_api.py

import uuid

from app.models.budget import BudgetEstimate
from app.models.place import Place
from app.models.trip import Trip, TripPlace
from app.services.place_service import get_or_create_place


def _make_trip(db, owner, with_children=True):
    """Inserts a trip straight into the DB (no geocoding, no budget engine)."""
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

    place = None
    if with_children:
        place, _ = get_or_create_place(
            db,
            name="Mysore Palace",
            city="Mysore",
            category="palace",
            latitude=12.3052,
            longitude=76.6552,
        )
        db.add(TripPlace(trip_id=trip.id, place_id=place.id, visit_order=1))
        db.add(
            TripPlace(
                trip_id=trip.id,
                custom_name="Hampi",
                custom_city="Hampi",
                latitude=15.335,
                longitude=76.46,
                visit_order=2,
            )
        )
        db.add(
            BudgetEstimate(
                trip_id=trip.id,
                hotel_cost=1000,
                food_cost=500,
                fuel_cost=300,
                misc_cost=200,
                total_cost=2000,
            )
        )
    db.commit()
    return trip, place


def test_delete_trip_removes_the_trip_and_everything_under_it(client, db_session, user, auth_headers):
    trip, place = _make_trip(db_session, user)
    trip_id, place_id = trip.id, place.id

    resp = client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)

    assert resp.status_code == 204
    assert db_session.query(Trip).filter(Trip.id == trip_id).count() == 0
    assert db_session.query(TripPlace).filter(TripPlace.trip_id == trip_id).count() == 0
    assert db_session.query(BudgetEstimate).filter(BudgetEstimate.trip_id == trip_id).count() == 0
    # The shared Place row must survive: only the trip's link to it goes away.
    assert db_session.query(Place).filter(Place.id == place_id).count() == 1


def test_delete_trip_leaves_the_users_other_trips_alone(client, db_session, user, auth_headers):
    doomed, _ = _make_trip(db_session, user)
    kept, _ = _make_trip(db_session, user)
    doomed_id, kept_id = doomed.id, kept.id

    client.delete(f"/api/v1/trips/{doomed_id}", headers=auth_headers)

    assert db_session.query(Trip).filter(Trip.id == kept_id).count() == 1
    assert db_session.query(TripPlace).filter(TripPlace.trip_id == kept_id).count() == 2


def test_delete_another_users_trip_returns_404_and_keeps_it(client, db_session, user, other_user, auth_headers):
    theirs, _ = _make_trip(db_session, other_user)
    theirs_id = theirs.id

    resp = client.delete(f"/api/v1/trips/{theirs_id}", headers=auth_headers)

    assert resp.status_code == 404
    assert db_session.query(Trip).filter(Trip.id == theirs_id).count() == 1


def test_delete_trip_without_a_token_is_rejected(client, db_session, user):
    trip, _ = _make_trip(db_session, user)
    trip_id = trip.id

    resp = client.delete(f"/api/v1/trips/{trip_id}")

    # Older FastAPI returns 403 here, newer versions 401. Both mean "rejected".
    assert resp.status_code in (401, 403)
    assert db_session.query(Trip).filter(Trip.id == trip_id).count() == 1


def test_delete_nonexistent_trip_returns_404(client, auth_headers):
    resp = client.delete(f"/api/v1/trips/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_trip_with_a_malformed_id_returns_422(client, auth_headers):
    resp = client.delete("/api/v1/trips/not-a-uuid", headers=auth_headers)
    assert resp.status_code == 422