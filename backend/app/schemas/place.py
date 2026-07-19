from pydantic import BaseModel
from uuid import UUID


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    category: str
    city: str
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}