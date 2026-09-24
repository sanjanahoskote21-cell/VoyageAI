# app/services/trip_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.trip import Trip, TripPlace
from app.models.place import Place
from app.models.budget import BudgetEstimate
from app.models.user import User
from app.schemas.trip import TripCreate
from app.services.route_optimizer import optimize_route, Point
from app.services.budget_service import calculate_budget
from app.services.geocoding_service import geocode_place, GeocodingError
from app.services.geo_utils import haversine_km


def geocode_place_name(place_name: str, city_hint: str | None = None) -> tuple[float, float, str]:
    """Returns (latitude, longitude, city) for a free-text place name.
    Same signature as before, so other callers (e.g. the custom-place endpoint) keep working.
    Raises ValueError if the place can't be found."""
    query = f"{place_name}, {city_hint}" if city_hint else place_name
    try:
        geo = geocode_place(query)
    except GeocodingError as exc:
        raise ValueError(str(exc)) from exc
    return geo["latitude"], geo["longitude"], city_hint or geo["city"]


def _geocode_or_400(location: str) -> tuple[float, float]:
    try:
        lat, lon, _ = geocode_place_name(location)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find location: {location}",
        )
    return lat, lon


def _tidy(name: str) -> str:
    """'bellary' -> 'Bellary'; leaves names the user already capitalised alone."""
    name = name.strip()
    return name.title() if name.islower() else name


def _sorted_places(trip: Trip) -> Trip:
    trip.trip_places.sort(key=lambda tp: (tp.visit_order is None, tp.visit_order))
    return trip


def _coords_for(db: Session, tp: TripPlace) -> tuple[float | None, float | None]:
    if tp.place_id:
        place = db.query(Place).filter(Place.id == tp.place_id).first()
        return place.latitude, place.longitude
    return tp.latitude, tp.longitude


def _apply_route_and_budget(
    db: Session,
    trip: Trip,
    start_lat: float,
    start_lon: float,
    end_coords: tuple[float, float] | None = None,
) -> None:
    """Route optimization + budget for ALL of a trip's places (seeded and custom).
    If end_coords is given, the drive from the last stop to the trip's end location
    is added to the total distance. Used by both create_trip and recalculate_trip
    so they can never disagree. Does not commit - the caller does."""
    trip_places = db.query(TripPlace).filter(TripPlace.trip_id == trip.id).all()

    if trip_places:
        points = []
        coords_by_id = {}
        for tp in trip_places:
            lat, lon = _coords_for(db, tp)
            if lat is None or lon is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"'{tp.custom_name or 'A place'}' has no coordinates, so it can't be routed.",
                )
            points.append(Point(id=str(tp.id), latitude=lat, longitude=lon))
            coords_by_id[str(tp.id)] = (lat, lon)

        start_point = Point(id="start", latitude=start_lat, longitude=start_lon)
        result = optimize_route(start_point, points)

        visit_order_map = {pid: i + 1 for i, pid in enumerate(result["ordered_place_ids"])}
        for tp in trip_places:
            tp.visit_order = visit_order_map.get(str(tp.id))

        total_km = result["optimized_distance_km"]
        if end_coords:
            last_lat, last_lon = coords_by_id[result["ordered_place_ids"][-1]]
            total_km += haversine_km(last_lat, last_lon, end_coords[0], end_coords[1])

        trip.total_distance_km = round(total_km, 2)
        trip.distance_saved_km = result["distance_saved_km"]
    else:
        trip.total_distance_km = None
        trip.distance_saved_km = None

    # Custom places carry a geocoded city, so they reach the budget engine too.
    trip_cities = list({tp.display_city for tp in trip_places if tp.display_city})
    budget_result = calculate_budget(
        db=db,
        cities=trip_cities,
        budget_tier=trip.budget_tier,
        num_days=trip.num_days,
        num_travelers=trip.num_travelers,
        total_distance_km=trip.total_distance_km or 0,
        travel_mode=trip.travel_mode,
    )

    if trip.budget_estimate:
        trip.budget_estimate.hotel_cost = budget_result["hotel_cost"]
        trip.budget_estimate.food_cost = budget_result["food_cost"]
        trip.budget_estimate.fuel_cost = budget_result["fuel_cost"]
        trip.budget_estimate.misc_cost = budget_result["misc_cost"]
        trip.budget_estimate.total_cost = budget_result["total_cost"]
    else:
        db.add(BudgetEstimate(
            trip_id=trip.id,
            hotel_cost=budget_result["hotel_cost"],
            food_cost=budget_result["food_cost"],
            fuel_cost=budget_result["fuel_cost"],
            misc_cost=budget_result["misc_cost"],
            total_cost=budget_result["total_cost"],
        ))


def recalculate_trip(db: Session, trip: Trip) -> None:
    """Recomputes route (visit_order, total/saved distance) and budget for a trip.
    Call this any time a trip's places change after creation."""
    start_lat, start_lon = _geocode_or_400(trip.start_location)

    # Older trips may have a free-text end like 'multiple destinations'.
    # If it can't be geocoded here, skip the end leg instead of blocking the update.
    end_coords = None
    if trip.end_location:
        try:
            end_lat, end_lon, _ = geocode_place_name(trip.end_location)
            end_coords = (end_lat, end_lon)
        except ValueError:
            end_coords = None

    _apply_route_and_budget(db, trip, start_lat, start_lon, end_coords)
    db.commit()


def create_trip(db: Session, user: User, trip_data: TripCreate) -> Trip:
    start_lat, start_lon = _geocode_or_400(trip_data.start_location)
    end_coords = _geocode_or_400(trip_data.end_location) if trip_data.end_location else None

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
            name = _tidy(place_input.custom_name)
            try:
                latitude, longitude, city = geocode_place_name(name, place_input.custom_city)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(exc),
                )
            trip_place = TripPlace(
                trip_id=new_trip.id,
                custom_name=name,
                custom_city=city,  # geocoded city is kept (it used to be thrown away)
                latitude=latitude,
                longitude=longitude,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each place must have either a place_id or a custom_name.",
            )

        db.add(trip_place)

    db.flush()

    _apply_route_and_budget(db, new_trip, start_lat, start_lon, end_coords)

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