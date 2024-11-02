from enum import Enum


class WeightUnit(Enum):
    KILOGRAMS = "kg"
    POUNDS = "lbs"


class SetType(Enum):
    WORKING = "working"
    WARMUP = "warmup"
