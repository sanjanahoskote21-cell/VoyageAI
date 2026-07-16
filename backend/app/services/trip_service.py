# app/services/trip_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.trip import Trip, TripPlace
from app.models.place import Place
from app.models.user import User
from app.schemas.trip import TripCreate


def geocode_place_name(name: str, city: str | None) -> tuple[float, float]:
    """
    Placeholder for Maps API geocoding integration.
    Will be implemented in the Maps integration phase.
    """
    raise NotImplementedError("Geocoding not yet implemented")


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
    db.flush()  # assigns new_trip.id without committing yet

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

    db.commit()
    db.refresh(new_trip)
    return new_trip


def get_trip(db: Session, user: User, trip_id: str) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found.",
        )
    return trip


def list_user_trips(db: Session, user: User) -> list[Trip]:
    return db.query(Trip).filter(Trip.user_id == user.id).order_by(Trip.created_at.desc()).all()