from uuid import UUID
from pydantic import BaseModel
from typing import Optional

from hard.models.tag import Tag


class ExerciseTemplate(BaseModel):
    id: UUID
    user_id: str
    tags: list[Tag]
    name: str
    image: Optional[str] = None