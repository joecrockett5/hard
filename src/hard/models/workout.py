from datetime import date
from typing import Optional

from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class Workout(BaseObject):
    object_type: ObjectType = ObjectType.WORKOUT
    date: date
    notes: Optional[str] = None
