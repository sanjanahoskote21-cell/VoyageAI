# app/models/trip.py

import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    start_location = Column(String, nullable=False)
    end_location = Column(String, nullable=True)
    num_days = Column(Integer, nullable=False)
    num_travelers = Column(Integer, nullable=False, default=1)
    budget_tier = Column(String, nullable=False)
    travel_mode = Column(String, nullable=False)

    total_distance_km = Column(Float, nullable=True)
    distance_saved_km = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="trips")
    trip_places = relationship("TripPlace", back_populates="trip", cascade="all, delete-orphan")
    budget_estimate = relationship("BudgetEstimate", back_populates="trip", uselist=False, cascade="all, delete-orphan")

class TripPlace(Base):
    __tablename__ = "trip_places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, index=True)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=True)

    custom_name = Column(String, nullable=True)
    custom_city = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    visit_order = Column(Integer, nullable=True)

    trip = relationship("Trip", back_populates="trip_places")
    place = relationship("Place")

    @property
    def display_name(self) -> str:
        """Returns the place's name, whether it's a database Place or a custom one."""
        return self.place.name if self.place else self.custom_name

    @property
    def display_city(self) -> str | None:
        return self.place.city if self.place else self.custom_city

    @property
    def resolved_latitude(self) -> float:
        return self.place.latitude if self.place else self.latitude

    @property
    def resolved_longitude(self) -> float:
        return self.place.longitude if self.place else self.longitude
    