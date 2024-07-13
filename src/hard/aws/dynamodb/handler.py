import os
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key

from hard.aws.dynamodb.base_object import DB_OBJECT_TYPE
from hard.aws.dynamodb.consts import DB_PARTITION, DB_SORT_KEY, PARTITION_TEMPLATE
from hard.aws.dynamodb.object_type import ObjectType
from hard.aws.models.user import User


class DynamoDB:
    def __init__(self, table_name: str) -> None:
        self._client = boto3.resource("dynamodb")
        self._table = self._client.Table(table_name)

    def query(
        self,
        /,
        key_expression,
        filter_expression=None,
        secondary_index_name: Optional[str] = None,
    ) -> list[dict[str]]:
        """
        Queries the DynamoDB table with the given expressions

        Use the `aws.dynamodb.Key` and `aws.dynamodb.Attr` objects
        to express the state of the desired keys and attributes

        You can additionally provide a `secondary_index_name` to
        search an alternate index
        """
        kwargs = {"KeyConditionExpression": key_expression}

        if filter_expression:
            kwargs.update({"FilterExpression": filter_expression})

        if secondary_index_name:
            kwargs.update({"IndexName": secondary_index_name})

        response = self._table.query(**kwargs)
        return response["Items"]

    def batch_get(self, /, user: User, object_cls, object_ids: list):
        partition = PARTITION_TEMPLATE.format(
            **{
                "user_id": user.id,
                "object_type": ObjectType.from_object_class(object_cls).value,
            }
        )
        items = self.query(
            key_expression=Key(DB_PARTITION).eq(partition),
            filter_expression=Attr("object_id").is_in(object_ids),
        )
        return items

    def put(self, /, data_object: DB_OBJECT_TYPE) -> DB_OBJECT_TYPE:
        """
        'Puts' the given `data_object` into the DynamoDB table
        """
        self._table.put_item(Item=data_object.to_db())
        return data_object

    def delete(self, /, data_object: DB_OBJECT_TYPE) -> DB_OBJECT_TYPE:
        """
        Deletes the given `data_object` from the DyanmoDB table
        """
        data = data_object.to_db()
        self._table.delete_item(
            Key={
                DB_PARTITION: data.get(DB_PARTITION),
                DB_SORT_KEY: data.get(DB_SORT_KEY),
            }
        )
        return data_object


def get_db_instance() -> DynamoDB:
    db_name = os.getenv("DYNAMO_TABLE_NAME")
    if db_name:
        return DynamoDB(table_name=db_name)
    raise ValueError("Missing Environment Variable: `DYNAMO_TABLE_NAME`")
