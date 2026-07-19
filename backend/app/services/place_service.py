from sqlalchemy.orm import Session
from app.models.place import Place


def search_places(db: Session, query: str | None = None, city: str | None = None) -> list[Place]:
    q = db.query(Place)
    if city:
        q = q.filter(Place.city.ilike(f"%{city}%"))
    if query:
        q = q.filter(Place.name.ilike(f"%{query}%"))
    return q.limit(20).all()