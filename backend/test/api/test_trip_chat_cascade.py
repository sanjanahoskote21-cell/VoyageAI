# backend/test/api/test_trip_chat_cascade.py
"""
Regression test: deleting a trip that has Travel Twin chat history used to
raise an IntegrityError, because chat_messages.trip_id is NOT NULL and the
relationship had no cascade. The fix is cascade="all, delete-orphan" on
Trip.chat_messages; these tests make sure it stays fixed.
"""
from app.models.chat_message import ChatMessage
from app.models.trip import Trip


def _trip_with_chat(db, owner, messages):
    trip = Trip(
        user_id=owner.id,
        start_location="Bengaluru",
        end_location="Hampi",
        num_days=3,
        num_travelers=2,
        budget_tier="mid",
        travel_mode="car",
    )
    db.add(trip)
    db.flush()
    for role, content in messages:
        db.add(ChatMessage(trip_id=trip.id, role=role, content=content))
    db.commit()
    return trip


def test_delete_trip_with_chat_history_removes_the_messages(client, db_session, user, auth_headers):
    trip = _trip_with_chat(
        db_session,
        user,
        [("user", "Best time to visit Hampi?"), ("assistant", "October to February is ideal.")],
    )
    trip_id = trip.id

    resp = client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)

    assert resp.status_code == 204
    assert db_session.query(Trip).filter(Trip.id == trip_id).count() == 0
    assert db_session.query(ChatMessage).filter(ChatMessage.trip_id == trip_id).count() == 0


def test_delete_trip_keeps_chat_history_of_other_trips(client, db_session, user, auth_headers):
    doomed = _trip_with_chat(db_session, user, [("user", "Hello")])
    kept = _trip_with_chat(db_session, user, [("user", "Hi"), ("assistant", "Hello there")])
    doomed_id, kept_id = doomed.id, kept.id

    client.delete(f"/api/v1/trips/{doomed_id}", headers=auth_headers)

    assert db_session.query(ChatMessage).filter(ChatMessage.trip_id == kept_id).count() == 2