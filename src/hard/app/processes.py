from hard.aws.dynamodb.base_object import DB_OBJECT_TYPE
from hard.aws.models.user import User


class RestProcesses:

    @staticmethod
    def get_list(
        object_cls: DB_OBJECT_TYPE,
        user: User,
    ) -> list[DB_OBJECT_TYPE]:
        pass

    @staticmethod
    def get(
        object_cls: DB_OBJECT_TYPE,
        user: User,
        object_id: str,
    ) -> DB_OBJECT_TYPE:
        pass

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
