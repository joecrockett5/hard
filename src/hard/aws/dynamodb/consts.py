from typing import TypeVar

from hard.models import Exercise, ExerciseJoin, Set, Tag, TagJoin, Workout

DB_PARTITION = "User_ObjectType"
DB_SORT_KEY = "Timestamp"
DELIMITER = "#"

PARTITION_TEMPLATE = "{user_id}" + DELIMITER + "{object_type}"

DB_OBJECT_TYPE = TypeVar(
    "DB_OBJECT_TYPE", Workout, Exercise, Set, Tag, TagJoin, ExerciseJoin
)
