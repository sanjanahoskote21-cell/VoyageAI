from pydantic import BaseModel, ConfigDict
from uuid import UUID


class RecommendedPlace(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: str
    city: str
    avg_rating: float | None
    latitude: float
    longitude: float
    final_score: float
    rating_score: float
    category_score: float
    proximity_score: float