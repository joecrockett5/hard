from typing import Optional
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.handler import get_db_instance
from hard.aws.dynamodb.object_type import ObjectType


class TagJoin(BaseObject):
    object_type: ObjectType = ObjectType.TAG_JOIN
    target_id: UUID
    tag_id: UUID
    target_object_type: Optional[ObjectType] = Field(default=None)

    # target_id handler
    @field_serializer("target_id")
    def target_id_to_str(self, target_id: UUID) -> str:
        return str(target_id)

    # tag_id handler
    @field_serializer("tag_id")
    def tag_id_to_str(self, tag_id: UUID) -> str:
        return str(tag_id)

    # target_object_type handler
    @field_serializer("target_object_type")
    def target_object_type_to_str(self, target_object_type: ObjectType) -> str:
        return target_object_type.value

    def get_target_object_type_from_db() -> ObjectType:
        # TODO: For now, will just deal with passing the value through
        pass
