import os

DB_PARTITION = "User_ObjectType"
DB_SORT_KEY = "Timestamp"
DELIMITER = "#"

ITEM_INDEX_NAME = os.getenv("DYNAMO_ITEM_INDEX_NAME")

PARTITION_TEMPLATE = "{user_id}" + DELIMITER + "{object_type}"
