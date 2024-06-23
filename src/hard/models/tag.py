from uuid import UUID
from pydantic import BaseModel


class Tag(BaseModel):
    id: UUID
    user_id: str
    name: str
    color_hex: str
    for_sets: bool = False
    for_exercises: bool = False
    for_workouts: bool = False
