from datetime import date

from hard.aws.dynamodb.base_object import BaseObject


class Workout(BaseObject):
    date: date
    notes: str
