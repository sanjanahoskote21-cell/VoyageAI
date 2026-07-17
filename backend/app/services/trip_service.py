# app/services/trip_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.trip import Trip, TripPlace
from app.models.place import Place
from app.models.user import User
from app.schemas.trip import TripCreate
from app.services.route_optimizer import optimize_route, Point


def geocode_place_name(name: str, city: str | None) -> tuple[float, float]:
    raise NotImplementedError("Geocoding not yet implemented")


def _sorted_places(trip: Trip) -> Trip:
    """Sorts a trip's places by visit_order, pushing unordered ones to the end."""
    trip.trip_places.sort(key=lambda tp: (tp.visit_order is None, tp.visit_order))
    return trip


def create_trip(db: Session, user: User, trip_data: TripCreate) -> Trip:
    new_trip = Trip(
        user_id=user.id,
        start_location=trip_data.start_location,
        end_location=trip_data.end_location,
        num_days=trip_data.num_days,
        num_travelers=trip_data.num_travelers,
        budget_tier=trip_data.budget_tier,
        travel_mode=trip_data.travel_mode,
    )
    db.add(new_trip)
    db.flush()

    trip_places = []
    for place_input in trip_data.places:
        if place_input.place_id:
            place = db.query(Place).filter(Place.id == place_input.place_id).first()
            if not place:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Place with id {place_input.place_id} not found.",
                )
            trip_place = TripPlace(trip_id=new_trip.id, place_id=place.id)

        elif place_input.custom_name:
            latitude, longitude = geocode_place_name(
                place_input.custom_name, place_input.custom_city
            )
            trip_place = TripPlace(
                trip_id=new_trip.id,
                custom_name=place_input.custom_name,
                custom_city=place_input.custom_city,
                latitude=latitude,
                longitude=longitude,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each place must have either a place_id or a custom_name.",
            )

        db.add(trip_place)
        trip_places.append(trip_place)

    db.flush()  # ensures every trip_place has its id before optimization

    # --- Route optimization ---
    # TODO: once geocoding/Maps API is integrated, use the real start_location
    # coordinates as the anchor point instead of the first place in the list.
    points = []
    for tp in trip_places:
        if tp.place_id:
            place = db.query(Place).filter(Place.id == tp.place_id).first()
            points.append(Point(id=str(tp.id), latitude=place.latitude, longitude=place.longitude))
        else:
            points.append(Point(id=str(tp.id), latitude=tp.latitude, longitude=tp.longitude))

    if len(points) >= 2:
        start_point, remaining_points = points[0], points[1:]
        result = optimize_route(start_point, remaining_points)

        visit_order_map = {pid: i + 1 for i, pid in enumerate(result["ordered_place_ids"])}
        for tp in trip_places:
            if str(tp.id) in visit_order_map:
                tp.visit_order = visit_order_map[str(tp.id)]
            elif str(tp.id) == start_point.id:
                tp.visit_order = 0

        new_trip.total_distance_km = result["optimized_distance_km"]
        new_trip.distance_saved_km = result["distance_saved_km"]

    elif len(points) == 1:
        trip_places[0].visit_order = 0

    db.commit()
    db.refresh(new_trip)
    return _sorted_places(new_trip)


def get_trip(db: Session, user: User, trip_id: str) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    return _sorted_places(trip)


def list_user_trips(db: Session, user: User) -> list[Trip]:
    return db.query(Trip).filter(Trip.user_id == user.id).order_by(Trip.created_at.desc()).all()