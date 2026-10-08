# app/models/place.py

import uuid
from sqlalchemy import Column, String, Float, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)  # "temple" | "waterfall" | "museum" | "custom" etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city = Column(String, nullable=False, index=True)
    avg_rating = Column(Float, nullable=True)
    external_place_id = Column(String, unique=True, nullable=True, index=True)
    last_synced_at = Column(DateTime, nullable=True)
    source = Column(String, nullable=False, default="seeded", server_default="seeded")  # "seeded" | "user_added"

    __table_args__ = (
        # Same rule dedupe_places.py uses: lowercase + trimmed name and city.
        # The database enforces it, so no code path can create a duplicate.
        Index(
            "uq_places_name_city_norm",
            func.lower(func.btrim(name)),
            func.lower(func.btrim(city)),
            unique=True,
        ),
    )