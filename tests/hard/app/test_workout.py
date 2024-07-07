import boto3
import moto
import pytest

from hard.app.workout import processes
from hard.aws.dynamodb.consts import DB_PARTITION, DB_SORT_KEY, DELIMITER
from hard.aws.dynamodb.object_type import ObjectType
from hard.aws.models.user import User
from hard.models.workout import Workout

MOCK_USER_ID = "mock_user"
MOCK_DYNAMO_TABLE_NAME = "mock_table"
GSI_NAME = "ItemSearch"

MOCK_PK = f"{MOCK_USER_ID}{DELIMITER}{ObjectType.WORKOUT.value}"

MOCK_TABLE_ITEMS = [
    {
        DB_PARTITION: {"S": MOCK_PK},
        DB_SORT_KEY: {"S": "2024-05-06T00:00:00.000000"},
        "object_id": {"S": "0"},
        "workout_date": {"S": "2024-05-06"},
    },
    {
        DB_PARTITION: {"S": MOCK_PK},
        DB_SORT_KEY: {"S": "2024-07-06T00:00:00.000000"},
        "object_id": {"S": "1"},
        "workout_date": {"S": "2024-07-06"},
    },
]


@pytest.fixture
def mock_user() -> User:
    return User(id=MOCK_USER_ID, email="mock@user.com")


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
                    "IndexName": GSI_NAME,
                    "KeySchema": [{"AttributeName": "object_id", "KeyType": "RANGE"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )
        yield client


@pytest.fixture
def append_items_to_table(set_up_aws_resources):
    client = set_up_aws_resources

    for item in MOCK_TABLE_ITEMS:
        client.put_item(
            TableName=MOCK_DYNAMO_TABLE_NAME,
            Item=item,
        )


@pytest.mark.usefixtures("env_vars")
class TestCreateWorkout:

    def test_successful_creation(self, set_up_aws_resources):
        client = set_up_aws_resources

        test_workout = Workout.model_validate(
            {
                "user_id": MOCK_USER_ID,
                "timestamp": "2024-07-06T00:00:00.000000",
                "object_id": "0",
                "workout_date": "2024-07-06",
            }
        )
        res = processes.create_workout(test_workout)

        assert res == test_workout
        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]

        assert len(table_data) == 1

        workout_data = {
            key: value.get("S", None) for key, value in table_data[0].items()
        }
        workout_from_db = Workout.from_db(workout_data)

        assert workout_from_db.__dict__ == test_workout.__dict__


@pytest.mark.usefixtures("env_vars")
class TestListWorkouts:

    @pytest.mark.usefixtures("append_items_to_table")
    def test_successfully_list_results(self, mock_user: User):
        results = processes.list_workouts(mock_user)

        assert isinstance(results, list)
        assert len(MOCK_TABLE_ITEMS) > 0
        assert len(results) == len(MOCK_TABLE_ITEMS)

        for index, item in enumerate(results):
            assert isinstance(item, Workout)
            assert item.object_type == ObjectType.WORKOUT
            assert item.object_id == str(
                index
            )  # in `MOCK_TABLE_ITEMS` id is set to index

    @pytest.mark.usefixtures("set_up_aws_resources")
    def test_no_results(self, mock_user: User):
        results = processes.list_workouts(mock_user)

        assert isinstance(results, list)
        assert len(results) == 0
