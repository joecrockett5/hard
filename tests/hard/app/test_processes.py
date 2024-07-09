from copy import deepcopy
from datetime import datetime
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
def example_object() -> BaseObject:
    return BaseObject.model_validate(
        {
            "user_id": MOCK_USER_ID,
            "timestamp": "2024-07-06T00:00:00.000000",
            "object_id": EXAMPLE_OBJECT_ID,
        }
    )


@pytest.fixture
def add_example_object_to_db(
    processes,
    set_up_aws_resources,
    example_object,
) -> Generator[BaseObject, Any, Any]:
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
    def test_successful_fetch(self, processes, add_example_object_to_db):
        example_object = add_example_object_to_db

        result = processes.get(object_id=EXAMPLE_OBJECT_ID)

        assert isinstance(result, BaseObject)
        assert result.__dict__ == example_object.__dict__

    def test_item_doesnt_exist(self, processes):
        with pytest.raises(
            ItemNotFoundError,
            match=f"No `BaseObject` found with `object_id`: '{EXAMPLE_OBJECT_ID}'",
        ):
            result = processes.get(object_id=EXAMPLE_OBJECT_ID)


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestPut:

    @pytest.mark.dependency(depends=["CREATE"])
    def test_successful_update(self, processes, add_example_object_to_db):
        example_object = add_example_object_to_db

        updated_object = deepcopy(example_object)
        updated_object.timestamp = datetime.fromisoformat("2024-05-06T00:00:00.000000")

        result = processes.put(updated_object)

        assert isinstance(result, BaseObject)

        client = boto3.client("dynamodb")
        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]

        assert len(table_data) == 1

        object_data = {
            key: value.get("S", None) for key, value in table_data[0].items()
        }
        object_from_db = BaseObject.from_db(object_data)

        assert object_from_db.timestamp.isoformat() == "2024-05-06T00:00:00.000000"
        assert object_from_db.__dict__ == updated_object.__dict__

    def test_item_doesnt_exist(self, processes, example_object):
        updated_object = deepcopy(example_object)
        updated_object.timestamp = datetime.fromisoformat("2024-05-06T00:00:00.000000")

        with pytest.raises(
            ItemNotFoundError,
            match=f"No `BaseObject` found with `object_id`: '{EXAMPLE_OBJECT_ID}': Cannot Update",
        ):
            processes.put(updated_object)


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestDelete:

    @pytest.mark.dependency(depends=["CREATE"])
    @pytest.mark.usefixtures("add_example_object_to_db")
    def test_successful_delete(self, processes):
        client = boto3.client("dynamodb")

        table_data_before = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_before) == 1

        result = processes.delete(EXAMPLE_OBJECT_ID)
        assert isinstance(result, BaseObject)

        table_data_after = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_after) == 0

    def test_item_doesnt_exist(self, processes):
        with pytest.raises(
            ItemNotFoundError,
            match=f"No `BaseObject` found with `object_id`: '{EXAMPLE_OBJECT_ID}': Cannot Delete",
        ):
            processes.delete(EXAMPLE_OBJECT_ID)
        pass
