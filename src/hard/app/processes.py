from hard.aws.dynamodb.base_object import DB_OBJECT_TYPE
from hard.aws.dynamodb.consts import (
    DB_PARTITION,
    DB_SORT_KEY,
    ITEM_INDEX_NAME,
    ITEM_INDEX_PARTITION,
    PARTITION_TEMPLATE,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from hard.aws.dynamodb.handler import Attr, Key, get_db_instance
from hard.aws.dynamodb.object_type import ObjectType
from hard.aws.models.user import User


class RestProcesses:

    @staticmethod
    def get_list(
        object_cls: DB_OBJECT_TYPE,
        user: User,
    ) -> list[DB_OBJECT_TYPE]:
        db = get_db_instance()
        query = db.query(
            key_expression=Key(DB_PARTITION).eq(
                PARTITION_TEMPLATE.format(
                    **{
                        "user_id": user.id,
                        "object_type": ObjectType.from_object_class(object_cls).value,
                    }
                )
            )
        )
        results = [object_cls.from_db(item) for item in query]
        return results

    @staticmethod
    def get(
        object_cls: DB_OBJECT_TYPE,
        user: User,
        object_id: str,
    ) -> DB_OBJECT_TYPE:
        db = get_db_instance()
        query = db.query(
            secondary_index_name=ITEM_INDEX_NAME,
            key_expression=Key(ITEM_INDEX_PARTITION).eq(object_id),
        )
        try:
            item = query[0]
        except IndexError:
            raise ItemNotFoundError(
                f"No `{ObjectType.from_object_class(object_cls).value}` found with `object_id`: '{object_id}'"
            )
        result = object_cls.from_db(item)
        return result

    @staticmethod
    def post(
        object_cls: DB_OBJECT_TYPE,
        user: User,
        object: DB_OBJECT_TYPE,
    ) -> DB_OBJECT_TYPE:
        pass

    @staticmethod
    def put(
        object_cls: DB_OBJECT_TYPE,
        user: User,
        object: DB_OBJECT_TYPE,
    ) -> DB_OBJECT_TYPE:
        pass

    @staticmethod
    def delete(
        object_cls: DB_OBJECT_TYPE,
        user: User,
        object_id: str,
    ) -> DB_OBJECT_TYPE:
        pass
