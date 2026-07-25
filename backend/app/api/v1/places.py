from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.place import PlaceResponse
from app.services.place_service import search_places
from app.services.place_sync_service import sync_places_for_city
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/places", tags=["Places"])


@router.get("/", response_model=list[PlaceResponse])
def get_places(
    query: str | None = Query(default=None),
    city: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return search_places(db, query=query, city=city)


@router.post("/sync", response_model=list[PlaceResponse])
def sync_places(
    city: str = Query(...),
    query: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Pulls places for a city from Google Places (or curated mock data as a
    fallback — see google_places_client.py) and upserts them into the local
    places table. Requires auth since it writes to the database.
    """
    return sync_places_for_city(db, city=city, query=query)