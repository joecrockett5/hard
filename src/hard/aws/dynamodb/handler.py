import boto3
from boto3.dynamodb.conditions import Key, Attr


class DynamoDB:
    def __init__(self, table_name: str) -> None:
        self._client = boto3.client("dynamodb")
        self._table = self._client.Table(table_name)

    def query(self, /, key_expression, filter_expression) -> list[dict[str]]:
        """
        Queries the DynamoDB table with the given expressions
        
        Use the `aws.dynamodb.Key` and `aws.dynamodb.Attr` objects 
        to express the state of the desired keys and attributes
        """
        response = self._table.query(
            KeyConditionExpression=key_expression,
            FilterExpression=filter_expression,
        )
        return response["Items"]
    
    def get_item(self, /, key_state: dict[str, str]) -> dict[str]:
        response = self._table.get_item(
            Key=key_state
        )
        return response["Item"]
