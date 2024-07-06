from enum import Enum


class WeightUnit(Enum):
    KILOGRAMS = "kgs"
    POUNDS = "lbs"


from .exercise import Exercise
from .exercise_join import ExerciseJoin
from .set import Set
from .tag import Tag
from .tag_join import TagJoin
from .workout import Workout
