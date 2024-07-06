from datetime import date
from typing import Optional

from pydantic import field_serializer, field_validator

from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class Workout(BaseObject):
    object_type: ObjectType = ObjectType.WORKOUT
    date: date
    notes: Optional[str] = None

    @field_serializer("date")
    def to_isoformat(self, date: date) -> str:
        return date.to_isoformat()

    @field_validator("date")
    @classmethod
    def from_isoformat(cls, date_str: str) -> date:
        return date.fromisoformat(date_str)
