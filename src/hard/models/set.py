from uuid import UUID
from pydantic import BaseModel

from hard.models import WeightUnit
from hard.models.tag import Tag


class Set(BaseModel):
    id: UUID
    tags: list[Tag]
    notes: str
    reps: int
    weight: float
    unit: WeightUnit
