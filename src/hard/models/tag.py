from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class Tag(BaseObject):
    object_type: ObjectType = ObjectType.TAG
    name: str
    color_hex: str
    for_sets: bool = True
    for_exercises: bool = True
    for_workouts: bool = True
