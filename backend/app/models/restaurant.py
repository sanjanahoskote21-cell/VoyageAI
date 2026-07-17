# app/models/restaurant.py

import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    budget_tier = Column(String, nullable=False, index=True)  # "budget" | "mid" | "luxury"
    avg_cost_per_person_per_day = Column(Float, nullable=False)  # covers 3 meals/day estimate
    rating = Column(Float, nullable=True)