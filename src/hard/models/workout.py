from datetime import date

from hard.aws.dynamodb.base_object import BaseObject

class Workout(BaseObject):
    id: str
    date: date
    notes: str
