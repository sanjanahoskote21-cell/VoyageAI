# app/services/place_sync_service.py

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.place import Place
from app.services.google_places_client import search_google_places


def sync_places_for_city(db: Session, city: str, query: str | None = None) -> list[Place]:
    """
    Fetches places for a city (live Google Places, or mock fallback — see
    google_places_client.py) and upserts them into the local places table,
    deduping on external_place_id so re-running a sync doesn't create
    duplicates.
    """
    results = search_google_places(city=city, query=query)
    synced: list[Place] = []

    for r in results:
        existing = (
            db.query(Place)
            .filter(Place.external_place_id == r["external_place_id"])
            .first()
        )
        if existing:
            existing.name = r["name"]
            existing.category = r["category"]
            existing.avg_rating = r.get("rating")
            existing.last_synced_at = datetime.utcnow()
            synced.append(existing)
        else:
            new_place = Place(
                name=r["name"],
                category=r["category"],
                latitude=r["latitude"],
                longitude=r["longitude"],
                city=city,
                avg_rating=r.get("rating"),
                external_place_id=r["external_place_id"],
                last_synced_at=datetime.utcnow(),
            )
            db.add(new_place)
            synced.append(new_place)

    db.commit()
    for place in synced:
        db.refresh(place)

    return synced