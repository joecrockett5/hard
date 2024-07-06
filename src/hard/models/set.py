from pydantic import field_validator, field_serializer

from hard.models import WeightUnit
from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class Set(BaseObject):
    object_type: ObjectType = ObjectType.SET
    notes: str
    reps: int
    weight: float
    unit: WeightUnit

    @field_validator("unit")
    @classmethod
    def process_weight_unit(cls, weight_unit: str):
        return WeightUnit(weight_unit)

    @field_serializer("unit")
    def serialize_weight_unit(unit: WeightUnit):
        return unit.value
