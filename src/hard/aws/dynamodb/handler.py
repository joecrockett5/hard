import os
from typing import TypeVar

import boto3
from boto3.dynamodb.conditions import Attr, Key

from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.consts import DB_OBJECT_TYPE


class DynamoDB:
    def __init__(self, table_name: str) -> None:
        self._client = boto3.resource("dynamodb")
        self._table = self._client.Table(table_name)

    def query(self, /, key_expression, filter_expression=None) -> list[dict[str]]:
        """
        Queries the DynamoDB table with the given expressions

        Use the `aws.dynamodb.Key` and `aws.dynamodb.Attr` objects
        to express the state of the desired keys and attributes
        """
        if filter_expression:
            response = self._table.query(
                KeyConditionExpression=key_expression,
                FilterExpression=filter_expression,
            )
        else:
            response = self._table.query(KeyConditionExpression=key_expression)
        return response["Items"]

    def put(self, /, data_object: DB_OBJECT_TYPE) -> DB_OBJECT_TYPE:
        """
        'Puts' the given `data_object` into the DynamoDB table
        """
        self._table.put_item(Item=data_object.to_db())
        return data_object


def get_db_instance() -> DynamoDB:
    db_name = os.getenv("DYNAMO_TABLE_NAME")
    if db_name:
        return DynamoDB(table_name=db_name)
    raise ValueError("Missing Environment Variable: `DYNAMO_TABLE_NAME`")
