from pydantic import field_serializer, field_validator

from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType
from hard.models import SetType, WeightUnit


class Set(BaseObject):
    object_type: ObjectType = ObjectType.SET
    set_type: SetType
    weight: float
    unit: WeightUnit
    reps: float
    notes: str
    exercise_join_id: str

    @field_validator("unit")
    @classmethod
    def process_weight_unit(cls, weight_unit: str):
        return WeightUnit(weight_unit)

    @field_serializer("unit")
    def serialize_weight_unit(self, unit: WeightUnit):
        return unit.value
