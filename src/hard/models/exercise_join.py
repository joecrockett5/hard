from uuid import UUID

from pydantic import field_serializer

from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class ExerciseJoin(BaseObject):
    object_type: ObjectType = ObjectType.EXCERCISE_JOIN
    workout_id: UUID
    exercise_id: UUID

    # workout_id handler
    @field_serializer("workout_id")
    def workout_id_to_str(self, workout_id: UUID) -> str:
        return str(workout_id)

    # exercise_id handler
    @field_serializer("exercise_id")
    def exercise_id_to_str(self, exercise_id: UUID) -> str:
        return str(exercise_id)
