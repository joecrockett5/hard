from typing import Optional

from hard.aws.dynamodb.base_object import BaseObject


class Exercise(BaseObject):
    name: str
    image: Optional[str] = None