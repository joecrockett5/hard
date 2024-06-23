from uuid import UUID
from pydantic import BaseModel

from hard.models.set import Set


class Exercise(BaseModel):
    id: UUID
    template_id: UUID
    sets: list[Set]
