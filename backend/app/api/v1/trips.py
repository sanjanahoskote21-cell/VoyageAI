# app/api/v1/trips.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.trip import TripCreate, TripResponse
from app.services.trip_service import create_trip, get_trip, list_user_trips

router = APIRouter(prefix="/trips", tags=["Trips"])


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