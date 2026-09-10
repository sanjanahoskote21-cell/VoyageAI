# app/api/v1/trips.py

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.trip_service import add_custom_place
from app.models.trip import TripPlace

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.trip import TripCreate, TripResponse
from app.services.trip_service import create_trip, get_trip, list_user_trips
from fastapi import HTTPException
from app.services.recommendation_service import get_recommendations
from app.schemas.recommendation import RecommendedPlace

router = APIRouter(prefix="/trips", tags=["Trips"])


class CustomPlaceRequest(BaseModel):
    place_name: str


@router.post("/{trip_id}/places/custom")
def add_custom_place_to_trip(
    trip_id: UUID,
    payload: CustomPlaceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    place = add_custom_place(payload.place_name, db)
    trip_place = TripPlace(trip_id=trip_id, place_id=place.id)
    db.add(trip_place)
    db.commit()
    return {
        "place_id": place.id,
        "name": place.name,
        "latitude": place.latitude,
        "longitude": place.longitude,
    }

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