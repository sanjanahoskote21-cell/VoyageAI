# app/models/budget.py

import uuid
from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class BudgetEstimate(Base):
    __tablename__ = "budget_estimates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, unique=True)

    hotel_cost = Column(Float, nullable=False)
    food_cost = Column(Float, nullable=False)
    fuel_cost = Column(Float, nullable=False)
    misc_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

    trip = relationship("Trip", back_populates="budget_estimate", uselist=False)