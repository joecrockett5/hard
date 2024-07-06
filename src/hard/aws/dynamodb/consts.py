DB_PARTITION = "User_ObjectType"
DB_SORT_KEY = "Timestamp"
DELIMITER = "#"

PARTITION_TEMPLATE = "{user_id}" + DELIMITER + "{object_type}"
