# app/schemas/trip.py

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TripPlaceInput(BaseModel):
    place_id: Optional[UUID] = None
    custom_name: Optional[str] = None
    custom_city: Optional[str] = None


class TripCreate(BaseModel):
    start_location: str
    end_location: Optional[str] = None
    num_days: int
    num_travelers: int = 1
    budget_tier: str
    travel_mode: str
    places: list[TripPlaceInput]


class TripPlaceResponse(BaseModel):
    id: UUID
    display_name: str
    display_city: Optional[str] = None
    resolved_latitude: float
    resolved_longitude: float
    visit_order: Optional[int] = None

    model_config = {"from_attributes": True}

class BudgetEstimateResponse(BaseModel):
    hotel_cost: float
    food_cost: float
    fuel_cost: float
    misc_cost: float
    total_cost: float

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
    budget: Optional[BudgetEstimateResponse] = Field(default=None, validation_alias="budget_estimate")

    model_config = {"from_attributes": True, "populate_by_name": True}
