from copy import deepcopy
from typing import Any, Generator

import boto3
import pytest

from hard.app.processes import RestProcesses
from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.consts import (
    DB_PARTITION,
    DB_SORT_KEY,
    DELIMITER,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from hard.aws.dynamodb.object_type import ObjectType
from hard.aws.models.user import User
from hard.models.workout import Workout
from tests.hard.app.test_workout import EXAMPLE_WORKOUT_ID

from ...conftest import MOCK_DYNAMO_TABLE_NAME, MOCK_USER_ID

MOCK_PK = f"{MOCK_USER_ID}{DELIMITER}{ObjectType.BASE_OBJECT.value}"

MOCK_TABLE_ITEMS = [
    {
        DB_PARTITION: {"S": MOCK_PK},
        DB_SORT_KEY: {"S": "2024-05-06T00:00:00.000000"},
        "object_id": {"S": "0"},
    },
    {
        DB_PARTITION: {"S": MOCK_PK},
        DB_SORT_KEY: {"S": "2024-07-06T00:00:00.000000"},
        "object_id": {"S": "1"},
    },
]


@pytest.fixture
def processes():
    return RestProcesses(BaseObject)


@pytest.fixture
def append_items_to_table(set_up_aws_resources):
    client = set_up_aws_resources

    for item in MOCK_TABLE_ITEMS:
        client.put_item(
            TableName=MOCK_DYNAMO_TABLE_NAME,
            Item=item,
        )


EXAMPLE_OBJECT_ID = "0123"


@pytest.fixture
def example_object() -> Workout:
    return Workout.model_validate(
        {
            "user_id": MOCK_USER_ID,
            "timestamp": "2024-07-06T00:00:00.000000",
            "object_id": EXAMPLE_OBJECT_ID,
            "workout_date": "2024-07-06",
        }
    )


@pytest.fixture
def add_example_object_to_db(
    processes,
    set_up_aws_resources,
    example_object,
) -> Generator[Workout, Any, Any]:
    processes.post(example_object)
    yield example_object


@pytest.mark.dependency(name="CREATE")
@pytest.mark.usefixtures("env_vars")
class TestPost:

    def test_successful_creation(self, processes, set_up_aws_resources, example_object):
        client = set_up_aws_resources

        res = processes.post(example_object)

        assert res == example_object
        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]

        assert len(table_data) == 1

        object_data = {
            key: value.get("S", None) for key, value in table_data[0].items()
        }
        object_from_db = BaseObject.from_db(object_data)

        assert object_from_db.__dict__ == example_object.__dict__

    def test_item_already_exists(self, processes, set_up_aws_resources, example_object):
        client = set_up_aws_resources
        processes.post(example_object)

        table_data_before = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_before) == 1

        with pytest.raises(
            ItemAlreadyExistsError,
            match=f"Found `BaseObject` with `object_id`: '{EXAMPLE_OBJECT_ID}': Cannot Create",
        ):
            processes.post(example_object)

        table_data_after = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_after) == 1


@pytest.mark.usefixtures("env_vars")
class TestGetList:

    @pytest.mark.usefixtures("append_items_to_table")
    def test_successfully_list_results(self, processes, mock_user: User):
        results = processes.get_list(mock_user)

        assert isinstance(results, list)
        assert len(MOCK_TABLE_ITEMS) > 0
        assert len(results) == len(MOCK_TABLE_ITEMS)

        for index, item in enumerate(results):
            assert isinstance(item, BaseObject)
            assert item.object_type == ObjectType.BASE_OBJECT
            assert item.object_id == str(
                index
            )  # in `MOCK_TABLE_ITEMS` id is set to index

    @pytest.mark.usefixtures("set_up_aws_resources")
    def test_no_results(self, processes, mock_user: User):
        results = processes.get_list(mock_user)

        assert isinstance(results, list)
        assert len(results) == 0


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestGet:

    @pytest.mark.dependency(depends=["CREATE"])
    def test_successful_fetch(self, processes, add_example_workout_to_db):
        example_workout = add_example_workout_to_db

        result = processes.get(workout_id=EXAMPLE_WORKOUT_ID)

        assert isinstance(result, Workout)
        assert result.__dict__ == example_workout.__dict__

    def test_item_doesnt_exist(self):
        with pytest.raises(
            ItemNotFoundError,
            match=f"No `Workout` found with `object_id`: '{EXAMPLE_WORKOUT_ID}'",
        ):
            result = processes.get_workout(workout_id=EXAMPLE_WORKOUT_ID)


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestUpdateWorkout:

    @pytest.mark.dependency(depends=["CREATE"])
    def test_successful_update(self, add_example_workout_to_db):
        example_workout = add_example_workout_to_db

        updated_workout = deepcopy(example_workout)
        updated_workout.notes = "UPDATED"

        result = processes.update_workout(updated_workout)

        assert isinstance(result, Workout)

        client = boto3.client("dynamodb")
        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]

        assert len(table_data) == 1

        workout_data = {
            key: value.get("S", None) for key, value in table_data[0].items()
        }
        workout_from_db = Workout.from_db(workout_data)

        assert workout_from_db.notes == "UPDATED"
        assert workout_from_db.__dict__ == updated_workout.__dict__

    def test_item_doesnt_exist(self, example_workout):
        updated_workout = deepcopy(example_workout)
        updated_workout.notes = "UPDATED"

        with pytest.raises(
            ItemNotFoundError,
            match=f"No `Workout` found with `object_id`: '{EXAMPLE_WORKOUT_ID}': Cannot Update",
        ):
            processes.update_workout(updated_workout)


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestDeleteWorkout:

    @pytest.mark.dependency(depends=["CREATE"])
    @pytest.mark.usefixtures("add_example_workout_to_db")
    def test_successful_delete(self):
        client = boto3.client("dynamodb")

        table_data_before = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_before) == 1

        result = processes.delete_workout(EXAMPLE_WORKOUT_ID)
        assert isinstance(result, Workout)

        table_data_after = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_after) == 0

    def test_item_doesnt_exist(self):
        with pytest.raises(
            ItemNotFoundError,
            match=f"No `Workout` found with `object_id`: '{EXAMPLE_WORKOUT_ID}': Cannot Delete",
        ):
            processes.delete_workout(EXAMPLE_WORKOUT_ID)
        pass
