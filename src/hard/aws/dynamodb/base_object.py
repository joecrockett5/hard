from pydantic import BaseModel, field_validator, field_serializer
from pydantic_core import PydanticCustomError
from datetime import datetime
from dateutil import parser as date_parser

from hard.aws.dynamodb.object_type import ObjectType

DB_PARTITION = "User_ObjectType"
DELIMITER = "_"

PARTITION_TEMPLATE = "{user_id}" + DELIMITER + "{object_type}"


class BaseObject(BaseModel):
    """Base object for all items stored in DynamoDB"""

    user_id: str
    timestamp: datetime
    object_type: ObjectType
    object_id: str

    # `created` handling
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_iso_format(cls, iso_date: str) -> datetime:
        return date_parser.isoparse(iso_date)

    @field_serializer("timestamp")
    def convert_to_iso(timestamp: datetime):
        return timestamp.isoformat()

    # `object_type` handling
    @field_validator("object_type")
    @classmethod
    def get_enum(cls, object_type: str):
        return ObjectType(object_type)

    @field_serializer("object_type")
    def get_value(object_type: ObjectType):
        return object_type.value

    def to_db(self):
        as_dict = self.model_dump()
        partition_key = (
            f'{as_dict.pop("user_id")}{DELIMITER}{as_dict.pop("object_type")}'
        )
        as_dict[DB_PARTITION] = partition_key

        return as_dict

    @classmethod
    def from_db(cls, object: dict[str, str]):
        try:
            user_id, object_type = object.pop(DB_PARTITION).split(DELIMITER)
        except ValueError:
            raise ValueError(
                f"Invalid Partition: Object partition ({DB_PARTITION}) did not contain delimiter: {DELIMITER}"
            )
        except KeyError:
            raise KeyError(
                f"Missing Partition: Object did not contain partition key ({DB_PARTITION})"
            )

        object.update({"user_id": user_id, "object_type": object_type})

        return cls.model_validate(object)
