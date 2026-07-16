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

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="trips")
    trip_places = relationship("TripPlace", back_populates="trip", cascade="all, delete-orphan")


class TripPlace(Base):
    """
    A single stop on a trip — either linked to an existing Place,
    or a custom place the user typed (e.g. a hometown village or temple).
    """
    __tablename__ = "trip_places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, index=True)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=True)  # null if custom

    custom_name = Column(String, nullable=True)
    custom_city = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)   # filled in by geocoding if custom
    longitude = Column(Float, nullable=True)  # filled in by geocoding if custom

    visit_order = Column(Integer, nullable=True)  # set after route optimization runs

    trip = relationship("Trip", back_populates="trip_places")
    place = relationship("Place")
    