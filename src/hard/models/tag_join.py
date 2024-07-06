from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.object_type import ObjectType


class TagJoin(BaseObject):
    object_type: ObjectType = ObjectType.TAG_JOIN
    target_id: str
    tag_id: str
