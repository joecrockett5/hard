from hard.aws.dynamodb.base_object import BaseObject


class Tag(BaseObject):
    name: str
    color_hex: str
    for_sets: bool = True
    for_exercises: bool = True
    for_workouts: bool = True
