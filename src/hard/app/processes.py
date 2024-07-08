from hard.aws.dynamodb.base_object import DB_OBJECT_TYPE
from hard.aws.models.user import User


class RestProcesses:

    def __init__(self, object_class: DB_OBJECT_TYPE) -> None:
        self.object_class = object_class

    def get_list(self, user: User) -> list[DB_OBJECT_TYPE]:
        pass

    def get(self, user: User, object_id: str) -> DB_OBJECT_TYPE:
        pass

    def post(self, user: User, object: DB_OBJECT_TYPE) -> DB_OBJECT_TYPE:
        pass

    def put(self, user: User, object: DB_OBJECT_TYPE) -> DB_OBJECT_TYPE:
        pass

    def delete(self, user: User, object_id: str) -> DB_OBJECT_TYPE:
        pass
