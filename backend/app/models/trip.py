# app/models/trip.py

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
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
    budget_tier = Column(String, nullable=False)   # "budget" | "mid" | "luxury"
    travel_mode = Column(String, nullable=False)    # "car" | "bike" | "public_transport"

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to the owning user
    owner = relationship("User", backref="trips")
    