import boto3
import moto
import pytest

from hard.aws.dynamodb.consts import DB_PARTITION, DB_SORT_KEY, ITEM_INDEX_NAME
from hard.aws.models.user import User

MOCK_USER_ID = "mock_user"
FAKE_USER_ID = "fake_user"
MOCK_DYNAMO_TABLE_NAME = "mock_table"


@pytest.fixture
def mock_user() -> User:
    return User(id=MOCK_USER_ID, email="mock@user.com")


@pytest.fixture
def fake_user() -> User:
    return User(id=FAKE_USER_ID, email="fake@user.com")


@pytest.fixture
def env_vars():
    pytest.MonkeyPatch().setenv("DYNAMO_TABLE_NAME", MOCK_DYNAMO_TABLE_NAME)
    yield


@pytest.fixture
def set_up_aws_resources():
    with moto.mock_aws():
        client = boto3.client("dynamodb")
        client.create_table(
            TableName=MOCK_DYNAMO_TABLE_NAME,
            AttributeDefinitions=[
                {
                    "AttributeName": DB_PARTITION,
                    "AttributeType": "S",
                },
                {
                    "AttributeName": DB_SORT_KEY,
                    "AttributeType": "S",
                },
                {
                    "AttributeName": "object_id",
                    "AttributeType": "S",
                },
            ],
            KeySchema=[
                {
                    "AttributeName": DB_PARTITION,
                    "KeyType": "HASH",
                },
                {
                    "AttributeName": DB_SORT_KEY,
                    "KeyType": "RANGE",
                },
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": ITEM_INDEX_NAME,
                    "KeySchema": [{"AttributeName": "object_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )
        yield client
