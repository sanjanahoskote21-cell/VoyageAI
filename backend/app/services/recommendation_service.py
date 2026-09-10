from sqlalchemy.orm import Session
from uuid import UUID

from app.models.trip import Trip, TripPlace
from app.models.place import Place
from app.services.route_optimizer import haversine_distance, Point

PROXIMITY_RADIUS_KM = 50
TOP_N = 10

RATING_WEIGHT = 0.40
CATEGORY_WEIGHT = 0.35
PROXIMITY_WEIGHT = 0.25


def get_recommendations(trip_id: UUID, db: Session) -> list[dict]:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise ValueError("Trip not found")

    trip_places = (
        db.query(TripPlace)
        .filter(TripPlace.trip_id == trip_id)
        .all()
    )
    if not trip_places:
        return []

    existing_ids = {tp.place_id for tp in trip_places if tp.place_id}
    trip_categories = {tp.place.category for tp in trip_places if tp.place_id and tp.place}
    trip_points = [
        Point(id=str(tp.id), latitude=tp.resolved_latitude, longitude=tp.resolved_longitude)
        for tp in trip_places
    ]

    candidates = (
        db.query(Place)
        .filter(~Place.id.in_(existing_ids))
        .filter(Place.source == "seeded")
        .all()
    )

    scored = []
    for place in candidates:
        rating_score = (place.avg_rating or 0.0) / 5.0
        category_score = 1.0 if place.category in trip_categories else 0.0

        candidate_point = Point(id=str(place.id), latitude=place.latitude, longitude=place.longitude)
        nearest_km = min(haversine_distance(candidate_point, pt) for pt in trip_points)
        proximity_score = max(0.0, 1 - nearest_km / PROXIMITY_RADIUS_KM)

        final_score = (
            RATING_WEIGHT * rating_score
            + CATEGORY_WEIGHT * category_score
            + PROXIMITY_WEIGHT * proximity_score
        )

        scored.append({
            "id": place.id,
            "name": place.name,
            "category": place.category,
            "city": place.city,
            "avg_rating": place.avg_rating,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "final_score": round(final_score, 4),
            "rating_score": round(rating_score, 4),
            "category_score": round(category_score, 4),
            "proximity_score": round(proximity_score, 4),
        })

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:TOP_N]