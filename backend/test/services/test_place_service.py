# backend/tests/services/test_place_service.py

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.place import Place
from app.services import place_sync_service
from app.services.place_service import get_or_create_place


def _make(db, name="Mysore Palace", city="Mysore", **kwargs):
    return get_or_create_place(
        db,
        name=name,
        city=city,
        category=kwargs.pop("category", "palace"),
        latitude=kwargs.pop("latitude", 12.3052),
        longitude=kwargs.pop("longitude", 76.6552),
        **kwargs,
    )


def test_creates_a_new_place(db_session):
    place, created = _make(db_session)
    assert created is True
    assert db_session.query(Place).count() == 1
    assert place.name == "Mysore Palace"


def test_same_place_with_different_case_and_spaces_is_not_duplicated(db_session):
    first, _ = _make(db_session)
    second, created = _make(db_session, name="  MYSORE   palace ", city=" mysore")
    assert created is False
    assert second.id == first.id
    assert db_session.query(Place).count() == 1


def test_stored_name_is_trimmed_and_whitespace_collapsed(db_session):
    place, _ = _make(db_session, name="  Hampi   Virupaksha  Temple ", city=" Hampi ")
    assert place.name == "Hampi Virupaksha Temple"
    assert place.city == "Hampi"


def test_same_name_in_different_city_is_a_separate_place(db_session):
    _make(db_session, name="City Market", city="Mysore")
    _, created = _make(db_session, name="City Market", city="Bengaluru")
    assert created is True
    assert db_session.query(Place).count() == 2


def test_matching_external_place_id_returns_existing_place(db_session):
    first, _ = _make(db_session, external_place_id="ext-1")
    second, created = _make(db_session, name="Totally Different Name", external_place_id="ext-1")
    assert created is False
    assert second.id == first.id


def test_database_itself_rejects_a_duplicate_insert(db_session):
    # Bypass get_or_create_place on purpose: the DB constraint is the backstop.
    _make(db_session)
    db_session.add(
        Place(name="MYSORE PALACE ", city="mysore", category="x", latitude=0.0, longitude=0.0)
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_sync_links_to_a_seeded_row_instead_of_creating_a_duplicate(db_session, monkeypatch):
    # This is the original bug: a hand-seeded row (no external id) and a
    # synced row for the same place used to become two rows.
    seeded, _ = _make(db_session)
    assert seeded.external_place_id is None

    def fake_search(city, query=None):
        return [
            {
                "name": "MYSORE PALACE",
                "category": "palace",
                "latitude": 12.3052,
                "longitude": 76.6552,
                "rating": 4.7,
                "external_place_id": "ext-mysore-palace",
            }
        ]

    monkeypatch.setattr(place_sync_service, "search_google_places", fake_search)
    place_sync_service.sync_places_for_city(db_session, city="mysore")

    assert db_session.query(Place).count() == 1
    row = db_session.query(Place).one()
    assert row.id == seeded.id
    assert row.external_place_id == "ext-mysore-palace"
    assert row.avg_rating == 4.7