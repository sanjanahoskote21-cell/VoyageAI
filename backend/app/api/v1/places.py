from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.place import PlaceResponse
from app.services.place_service import search_places

router = APIRouter(prefix="/places", tags=["Places"])


@router.get("/", response_model=list[PlaceResponse])
def get_places(
    query: str | None = Query(default=None),
    city: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return search_places(db, query=query, city=city)