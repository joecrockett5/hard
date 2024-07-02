from enum import Enum


class WeightUnit(Enum):
    KILOGRAMS = "kgs"
    POUNDS = "lbs"


from .exercise import Exercise
from .set import Set
from .tag import Tag
from .workout import Workout
