# app/schemas/trip.py

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TripPlaceInput(BaseModel):
    """
    A single place the user wants to visit — either a reference
    to an existing Place, or a custom one they typed themselves.
    """
    place_id: Optional[UUID] = None       # set if picked from search
    custom_name: Optional[str] = None     # set if user typed a custom place
    custom_city: Optional[str] = None     # optional, helps with geocoding later


class TripCreate(BaseModel):
    start_location: str
    end_location: Optional[str] = None
    num_days: int
    num_travelers: int = 1
    budget_tier: str          # "budget" | "mid" | "luxury"
    travel_mode: str          # "car" | "bike" | "public_transport"
    places: list[TripPlaceInput]


class TripPlaceResponse(BaseModel):
    id: UUID
    display_name: str
    display_city: Optional[str] = None
    resolved_latitude: float
    resolved_longitude: float
    visit_order: Optional[int] = None

    model_config = {"from_attributes": True}


class TripResponse(BaseModel):
    id: UUID
    start_location: str
    end_location: Optional[str]
    num_days: int
    num_travelers: int
    budget_tier: str
    travel_mode: str
    total_distance_km: Optional[float] = None
    distance_saved_km: Optional[float] = None
    created_at: datetime
    places: list[TripPlaceResponse] = Field(default=[], validation_alias="trip_places")

    model_config = {"from_attributes": True, "populate_by_name": True}