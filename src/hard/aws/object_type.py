from enum import Enum, auto


class ObjectType(Enum):
    TAG = "tag"
    TAG_JOIN = "tag_join"
    WORKOUT = "workout"
    EXERCISE = "exercise"
    SET = "set"