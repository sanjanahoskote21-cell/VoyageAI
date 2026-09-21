# app/api/v1/trips.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.trip import Trip, TripPlace
from app.models.place import Place
from app.schemas.trip import TripCreate, TripResponse, TripPlaceResponse
from app.services.trip_service import (
    create_trip,
    get_trip,
    list_user_trips,
    geocode_place_name,
    recalculate_trip,
)
from app.services.recommendation_service import get_recommendations
from app.schemas.recommendation import RecommendedPlace

router = APIRouter(prefix="/trips", tags=["Trips"])


class CustomPlaceRequest(BaseModel):
    place_name: str
    city_hint: str | None = None


@router.post("/{trip_id}/places/custom", response_model=TripPlaceResponse)
def add_custom_place_to_trip(
    trip_id: UUID,
    payload: CustomPlaceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    try:
        latitude, longitude, resolved_city = geocode_place_name(payload.place_name, payload.city_hint)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Could not find location: {payload.place_name}",
        )

    trip_place = TripPlace(
        trip_id=trip_id,
        custom_name=payload.place_name,
        custom_city=payload.city_hint or resolved_city,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(trip_place)
    db.commit()
    db.refresh(trip_place)

    recalculate_trip(db, trip)
    db.refresh(trip_place)

    return trip_place


@router.post("/{trip_id}/places/{place_id}", response_model=TripPlaceResponse)
def add_place_to_trip(
    trip_id: UUID,
    place_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found.")

    trip_place = TripPlace(trip_id=trip_id, place_id=place.id)
    db.add(trip_place)
    db.commit()
    db.refresh(trip_place)

    recalculate_trip(db, trip)
    db.refresh(trip_place)

    return trip_place


@router.delete("/{trip_id}/places/{trip_place_id}", status_code=204)
def remove_place_from_trip(
    trip_id: UUID,
    trip_place_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    trip_place = (
        db.query(TripPlace)
        .filter(TripPlace.id == trip_place_id, TripPlace.trip_id == trip_id)
        .first()
    )
    if not trip_place:
        raise HTTPException(status_code=404, detail="Place not found on this trip.")

    db.delete(trip_place)
    db.commit()

    recalculate_trip(db, trip)

    return None


@router.get("/{trip_id}/recommendations", response_model=list[RecommendedPlace])
def get_trip_recommendations(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_recommendations(trip_id, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Trip not found")


@router.post("/", response_model=TripResponse, status_code=201)
def create_new_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_trip(db, current_user, trip_data)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip_by_id(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_trip(db, current_user, trip_id)


@router.get("/", response_model=list[TripResponse])
def list_my_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_user_trips(db, current_user)