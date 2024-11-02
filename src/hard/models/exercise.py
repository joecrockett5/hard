from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class Exercise(BaseObject):
    object_type: ObjectType = ObjectType.EXERCISE
    name: str
    description: str
