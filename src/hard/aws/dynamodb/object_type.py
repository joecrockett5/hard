from enum import Enum


class ObjectType(Enum):
    # Objects
    BASE_OBJECT = "base_object"
    TAG = "tag"
    WORKOUT = "workout"
    EXERCISE = "exercise"
    SET = "set"

    # Joins
    TAG_JOIN = "tag_join"
    EXCERCISE_JOIN = "exercise_join"
