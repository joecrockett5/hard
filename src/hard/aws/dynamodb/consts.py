DB_PARTITION = "User_ObjectType"
DB_SORT_KEY = "Timestamp"
DELIMITER = "#"

ITEM_INDEX_NAME = "ItemSearch"
ITEM_INDEX_PARTITION = "object_id"

PARTITION_TEMPLATE = "{user_id}" + DELIMITER + "{object_type}"


class ItemNotFoundError(Exception):
    pass


class ItemAlreadyExistsError(Exception):
    pass


class ItemAccessUnauthorizedError(Exception):
    pass
