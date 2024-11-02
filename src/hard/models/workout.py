from datetime import date

from pydantic import field_serializer, field_validator

from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class Workout(BaseObject):
    object_type: ObjectType = ObjectType.WORKOUT
    workout_date: date
    notes: str
    title: str

    @field_serializer("workout_date")
    def to_isoformat(self, workout_date: date) -> str:
        return workout_date.isoformat()

    @field_validator("workout_date", mode="before")
    @classmethod
    def from_isoformat(cls, date_str: str) -> date:
        return date.fromisoformat(date_str)
