# app/services/place_sync_service.py

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.place import Place
from app.services.google_places_client import search_google_places
from app.services.place_service import get_or_create_place


def sync_places_for_city(db: Session, city: str, query: str | None = None) -> list[Place]:
    """
    Fetches places for a city (live Google Places, or mock fallback — see
    google_places_client.py) and upserts them into the local places table.

    Matching is by external_place_id first, then by normalized name + city.
    The second match is what links a hand-seeded row to its synced twin
    instead of creating a duplicate; the seeded row adopts the
    external_place_id.
    """
    results = search_google_places(city=city, query=query)
    synced: list[Place] = []

    for r in results:
        place, created = get_or_create_place(
            db,
            name=r["name"],
            city=city,
            category=r["category"],
            latitude=r["latitude"],
            longitude=r["longitude"],
            avg_rating=r.get("rating"),
            external_place_id=r["external_place_id"],
            source="seeded",
        )
        if not created:
            place.category = r["category"]
            place.avg_rating = r.get("rating")
            if place.external_place_id is None:
                place.external_place_id = r["external_place_id"]
        # Naive UTC, because the last_synced_at column is timezone-naive.
        place.last_synced_at = datetime.now(timezone.utc).replace(tzinfo=None)
        synced.append(place)

    db.commit()
    for place in synced:
        db.refresh(place)

    return synced