from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class ExerciseJoin(BaseObject):
    object_type: ObjectType = ObjectType.EXCERCISE_JOIN
    workout_id: str
    exercise_id: str
