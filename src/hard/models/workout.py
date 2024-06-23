from uuid import UUID
from pydantic import BaseModel
from datetime import date

from hard.models.tag import Tag
from hard.models.exercise import Exercise


class Workout(BaseModel):
    id: UUID
    user_id: str
    tags: list[Tag]
    date: date
    exercises: list[Exercise]
    notes: str