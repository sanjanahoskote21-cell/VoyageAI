from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.place import Place


def clean_text(value: str) -> str:
    """Trim and collapse inner whitespace. This is what gets stored."""
    return " ".join(value.split())


def normalize_key(value: str) -> str:
    """Comparison key. MUST stay equal to lower(btrim(...)) in the DB index
    and to the key in scripts/dedupe_places.py."""
    return value.strip().lower()


def find_place(
    db: Session, name: str, city: str, external_place_id: str | None = None
) -> Place | None:
    if external_place_id:
        by_external = (
            db.query(Place).filter(Place.external_place_id == external_place_id).first()
        )
        if by_external:
            return by_external
    return (
        db.query(Place)
        .filter(
            func.lower(func.btrim(Place.name)) == normalize_key(name),
            func.lower(func.btrim(Place.city)) == normalize_key(city),
        )
        .first()
    )


def get_or_create_place(
    db: Session,
    *,
    name: str,
    city: str,
    category: str,
    latitude: float,
    longitude: float,
    avg_rating: float | None = None,
    external_place_id: str | None = None,
    source: str = "seeded",
) -> tuple[Place, bool]:
    """The ONLY way code should create a Place. Returns (place, created).
    Does not commit; the caller commits."""
    name, city = clean_text(name), clean_text(city)

    place = find_place(db, name, city, external_place_id)
    if place:
        return place, False

    try:
        # Savepoint: if two requests race, only this insert is rolled back.
        with db.begin_nested():
            place = Place(
                name=name,
                city=city,
                category=category,
                latitude=latitude,
                longitude=longitude,
                avg_rating=avg_rating,
                external_place_id=external_place_id,
                source=source,
            )
            db.add(place)
            db.flush()
    except IntegrityError:
        place = find_place(db, name, city, external_place_id)
        if place is None:
            raise
        return place, False

    return place, True


def search_places(db: Session, query: str | None = None, city: str | None = None) -> list[Place]:
    q = db.query(Place)
    if city:
        q = q.filter(Place.city.ilike(f"%{city}%"))
    if query:
        q = q.filter(Place.name.ilike(f"%{query}%"))
    return q.limit(20).all()