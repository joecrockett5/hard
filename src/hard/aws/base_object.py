from pydantic import BaseModel, field_validator, field_serializer
from datetime import datetime
from dateutil import parser as date_parser

from hard.aws.object_type import ObjectType


class BaseObject(BaseModel):
    """Base object for all items stored in DynamoDB"""
    user_id: str
    created: datetime
    object_type: ObjectType
    object_id: str

    # `created` handling
    @field_validator("created", mode="before")
    @classmethod
    def parse_iso_format(cls, iso_date: str) -> datetime:
        return date_parser.isoparse(iso_date)
    
    @field_serializer("created")
    def convert_to_iso(created: datetime):
        return created.isoformat()
    
    # `object_type` handling
    @field_validator("object_type")
    @classmethod
    def get_enum(cls, object_type: str):
        return ObjectType(object_type)

    @field_serializer("object_type")
    def get_value(object_type: ObjectType):
        return object_type.value