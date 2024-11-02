from datetime import datetime
from typing import Optional, TypeVar
from uuid import UUID, uuid4

from dateutil import parser as date_parser
from pydantic import BaseModel, field_serializer, field_validator

from hard.aws.dynamodb.consts import DB_PARTITION, DB_SORT_KEY, DELIMITER
from hard.aws.dynamodb.object_type import ObjectType
from hard.aws.models.user import User

CORE_ATTRIBUTES = ["user_id", "timestamp", "object_type", "object_id"]


class BaseObject(BaseModel):
    """Base object for all items stored in DynamoDB"""

    user_id: Optional[str]
    timestamp: Optional[datetime]
    object_type: Optional[ObjectType]
    object_id: Optional[UUID] = None

    # `created` handling
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_iso_format(cls, iso_date: str | None) -> datetime | None:
        if iso_date is None:
            return None
        return date_parser.isoparse(iso_date)

    @field_serializer("timestamp")
    def convert_to_iso(self, timestamp: datetime):
        return timestamp.isoformat()

    # `object_type` handling
    @field_validator("object_type")
    @classmethod
    def get_enum(cls, object_type: str | None):
        if object_type != None:
            return ObjectType(object_type)
        else:
            return None

    @field_serializer("object_type")
    def get_value(self, object_type: ObjectType | None):
        if object_type == None:
            return None
        return object_type.value

    # `object_id` handling
    @field_serializer("object_id")
    def to_str(self, object_id: UUID):
        return str(object_id)

    def to_db(self):
        as_dict = self.model_dump()
        partition_key = (
            f'{as_dict.pop("user_id")}{DELIMITER}{as_dict.pop("object_type")}'
        )
        as_dict[DB_PARTITION] = partition_key
        as_dict[DB_SORT_KEY] = as_dict.pop("timestamp")

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
        object.update({"timestamp": object.pop(DB_SORT_KEY)})

        return cls.model_validate(object)

    def from_request(self, user: User, object_type: ObjectType):
        self.set_owner(user)
        self.set_object_type(object_type)
        return

    def init_from_request(self, user: User, object_type: ObjectType):
        self.set_owner(user)
        self.set_object_type(object_type)
        self.generate_id()
        self.timestamp = datetime.now()
        return

    def owned_by(self, user: User):
        return self.user_id == user.id

    def generate_id(self) -> UUID:
        if self.object_id is not None:
            # By this point, the item should have been assigned an `object_type`
            raise ReferenceError(
                f"`{self.object_type.value}` Item already has an `object_id`"
            )
        new_id = uuid4()
        self.object_id = new_id
        return new_id

    def set_owner(self, user: User):
        self.user_id = user.id

    def set_object_type(self, object_type: ObjectType):
        self.object_type = object_type


DB_OBJECT_TYPE = TypeVar("DB_OBJECT_TYPE", bound=BaseObject)
