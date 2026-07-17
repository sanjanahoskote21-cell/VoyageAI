# app/models/hotel.py

import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    budget_tier = Column(String, nullable=False, index=True)  # "budget" | "mid" | "luxury"
    price_per_night = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)