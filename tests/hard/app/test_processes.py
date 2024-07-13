import re
from copy import deepcopy
from datetime import datetime
from typing import Any, Generator
from uuid import uuid4

import boto3
import pytest

from hard.app import processes as processes_module
from hard.aws.dynamodb.base_object import BaseObject
from hard.aws.dynamodb.consts import (
    DB_PARTITION,
    DB_SORT_KEY,
    DELIMITER,
    InvalidAttributeChangeError,
    ItemAccessUnauthorizedError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from hard.aws.dynamodb.object_type import ObjectType
from hard.models.exercise_join import ExerciseJoin
from hard.models.tag_join import TagJoin
from hard.models.workout import Workout

from ...conftest import MOCK_DYNAMO_TABLE_NAME, MOCK_USER_ID

MOCK_PK = f"{MOCK_USER_ID}{DELIMITER}{ObjectType.BASE_OBJECT.value}"

MOCK_TABLE_ITEMS = [
    {
        DB_PARTITION: {"S": MOCK_PK},
        DB_SORT_KEY: {"S": "2024-05-06T00:00:00.000000"},
        "object_id": {"S": str(uuid4())},
    },
    {
        DB_PARTITION: {"S": MOCK_PK},
        DB_SORT_KEY: {"S": "2024-07-06T00:00:00.000000"},
        "object_id": {"S": str(uuid4())},
    },
]


@pytest.fixture
def processes():
    return processes_module.RestProcesses()


@pytest.fixture
def append_items_to_table(set_up_aws_resources):
    client = set_up_aws_resources

    for item in MOCK_TABLE_ITEMS:
        client.put_item(
            TableName=MOCK_DYNAMO_TABLE_NAME,
            Item=item,
        )


EXAMPLE_OBJECT_ID = str(uuid4())


@pytest.fixture
def example_object() -> BaseObject:
    return BaseObject.model_validate(
        {
            "user_id": MOCK_USER_ID,
            "timestamp": "2024-07-06T00:00:00.000000",
            "object_id": EXAMPLE_OBJECT_ID,
            "object_type": ObjectType.BASE_OBJECT,
        }
    )


@pytest.fixture
def add_example_object_to_db(
    processes,
    set_up_aws_resources,
    example_object,
    mock_user,
) -> Generator[BaseObject, Any, Any]:
    processes.post(BaseObject, mock_user, example_object)
    yield example_object


@pytest.mark.dependency(name="CREATE")
@pytest.mark.usefixtures("env_vars")
class TestPost:

    def test_successful_creation(
        self, mock_user, processes, set_up_aws_resources, example_object
    ):
        client = set_up_aws_resources

        res = processes.post(BaseObject, mock_user, example_object)

        assert res == example_object
        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]

        assert len(table_data) == 1

        object_data = {
            key: value.get("S", None) for key, value in table_data[0].items()
        }
        object_from_db = BaseObject.from_db(object_data)

        assert object_from_db.__dict__ == example_object.__dict__

    def test_item_already_exists(
        self, mock_user, processes, set_up_aws_resources, example_object
    ):
        client = set_up_aws_resources
        processes.post(BaseObject, mock_user, example_object)

        table_data_before = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_before) == 1

        with pytest.raises(
            ItemAlreadyExistsError,
            match=f"Found `BaseObject` with `object_id`: '{EXAMPLE_OBJECT_ID}': Cannot Create",
        ):
            processes.post(BaseObject, mock_user, example_object)

        table_data_after = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_after) == 1

    def test_user_mismatch(
        self, fake_user, processes, set_up_aws_resources, example_object
    ):
        client = set_up_aws_resources

        with pytest.raises(
            ItemAccessUnauthorizedError,
            match=re.escape(
                f"`{example_object.object_type.value}` Item not owned by current user ({fake_user.id}): Cannot Create"
            ),
        ):
            processes.post(BaseObject, fake_user, example_object)

        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data) == 0


@pytest.mark.usefixtures("env_vars")
class TestGetList:

    @pytest.mark.usefixtures("append_items_to_table")
    def test_successfully_list_results(self, mock_user, processes):
        results = processes.get_list(BaseObject, mock_user)

        assert isinstance(results, list)
        assert len(MOCK_TABLE_ITEMS) > 0
        assert len(results) == len(MOCK_TABLE_ITEMS)

        for item in results:
            assert isinstance(item, BaseObject)
            assert item.object_type == ObjectType.BASE_OBJECT

    @pytest.mark.usefixtures("set_up_aws_resources")
    def test_no_results(self, mock_user, processes):
        results = processes.get_list(BaseObject, mock_user)

        assert isinstance(results, list)
        assert len(results) == 0


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestGet:

    @pytest.mark.dependency(depends=["CREATE"])
    def test_successful_fetch(self, mock_user, processes, add_example_object_to_db):
        example_object = add_example_object_to_db

        result = processes.get(BaseObject, mock_user, object_id=EXAMPLE_OBJECT_ID)

        assert isinstance(result, BaseObject)
        assert result.__dict__ == example_object.__dict__

    def test_item_doesnt_exist(self, mock_user, processes):
        with pytest.raises(
            ItemNotFoundError,
            match=f"No `BaseObject` found with `object_id`: '{EXAMPLE_OBJECT_ID}'",
        ):
            result = processes.get(BaseObject, mock_user, object_id=EXAMPLE_OBJECT_ID)

    def test_user_mismatch(self, fake_user, processes, add_example_object_to_db):
        example_object = add_example_object_to_db

        with pytest.raises(
            ItemAccessUnauthorizedError,
            match=re.escape(
                f"`{example_object.object_type.value}` Item not owned by current user ({fake_user.id}): Cannot Fetch"
            ),
        ):
            processes.get(BaseObject, fake_user, EXAMPLE_OBJECT_ID)


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestPut:

    @pytest.mark.dependency(depends=["CREATE"])
    def test_successful_update(self, mock_user, processes):
        example_object = Workout.model_validate(
            {
                "object_id": str(uuid4()),
                "timestamp": "2024-05-06T00:00:00.000000",
                "user_id": MOCK_USER_ID,
                "workout_date": "2024-05-06",
            }
        )
        processes.post(Workout, mock_user, example_object)

        updated_object = deepcopy(example_object)
        updated_object.notes = "UPDATED"

        result = processes.put(Workout, mock_user, updated_object)

        assert isinstance(result, Workout)

        client = boto3.client("dynamodb")
        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]

        assert len(table_data) == 1

        object_data = {
            key: value.get("S", None) for key, value in table_data[0].items()
        }
        object_from_db = Workout.from_db(object_data)

        assert object_from_db.notes == "UPDATED"
        assert object_from_db.__dict__ == updated_object.__dict__

    def test_item_doesnt_exist(self, mock_user, processes, example_object):
        updated_object = deepcopy(example_object)
        updated_object.timestamp = datetime.fromisoformat("2024-05-06T00:00:00.000000")

        with pytest.raises(
            ItemNotFoundError,
            match=f"No `BaseObject` found with `object_id`: '{EXAMPLE_OBJECT_ID}': Cannot Update",
        ):
            processes.put(BaseObject, mock_user, updated_object)

    @pytest.mark.dependency(depends=["CREATE"])
    def test_user_mismatch(self, mock_user, fake_user, processes):
        example_object = Workout.model_validate(
            {
                "object_id": str(uuid4()),
                "timestamp": "2024-05-06T00:00:00.000000",
                "user_id": MOCK_USER_ID,
                "workout_date": "2024-05-06",
            }
        )
        processes.post(Workout, mock_user, example_object)

        updated_object = deepcopy(example_object)
        updated_object.notes = "UPDATED"

        with pytest.raises(
            ItemAccessUnauthorizedError,
            match=re.escape(
                f"`{example_object.object_type.value}` Item not owned by current user ({fake_user.id}): Cannot Update"
            ),
        ):
            processes.put(Workout, fake_user, updated_object)

        client = boto3.client("dynamodb")
        table_data = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]

        assert len(table_data) == 1

        object_data = {
            key: value.get("S", None) for key, value in table_data[0].items()
        }
        object_from_db = Workout.from_db(object_data)

        assert object_from_db.notes == None
        assert object_from_db.__dict__ == example_object.__dict__

    def test_invalid_attr_change(self, mock_user, processes, add_example_object_to_db):
        example_object = add_example_object_to_db

        updated_object = deepcopy(example_object)
        updated_object.timestamp = datetime.fromisoformat("2024-05-06T00:00:00.000000")

        with pytest.raises(
            InvalidAttributeChangeError,
            match=f"Cannot Modify `timestamp` Attribute on `{example_object.object_type.value}`",
        ):
            processes.put(BaseObject, mock_user, updated_object)


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestDelete:

    @pytest.mark.dependency(depends=["CREATE"])
    @pytest.mark.usefixtures("add_example_object_to_db")
    def test_successful_delete(self, mock_user, processes):
        client = boto3.client("dynamodb")

        table_data_before = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_before) == 1

        result = processes.delete(BaseObject, mock_user, EXAMPLE_OBJECT_ID)
        assert isinstance(result, BaseObject)

        table_data_after = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_after) == 0

    def test_item_doesnt_exist(self, mock_user, processes):
        with pytest.raises(
            ItemNotFoundError,
            match=f"No `BaseObject` found with `object_id`: '{EXAMPLE_OBJECT_ID}': Cannot Delete",
        ):
            processes.delete(BaseObject, mock_user, EXAMPLE_OBJECT_ID)

    @pytest.mark.dependency(depends=["CREATE"])
    def test_user_mismatch(self, fake_user, processes, add_example_object_to_db):
        example_object = add_example_object_to_db
        client = boto3.client("dynamodb")

        table_data_before = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_before) == 1

        with pytest.raises(
            ItemAccessUnauthorizedError,
            match=re.escape(
                f"`{example_object.object_type.value}` Item not owned by current user ({fake_user.id}): Cannot Delete"
            ),
        ):
            processes.delete(BaseObject, fake_user, EXAMPLE_OBJECT_ID)

        table_data_after = client.scan(TableName=MOCK_DYNAMO_TABLE_NAME)["Items"]
        assert len(table_data_after) == 1


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestExerciseJoinFilter:

    @pytest.mark.dependency(depends=["CREATE"])
    def test_successful_retrieval(self, mock_user, processes):
        MOCK_EXERCISE_ID = uuid4()
        MOCK_WORKOUT_ID = uuid4()

        mock_join = ExerciseJoin.model_validate(
            {
                "user_id": MOCK_USER_ID,
                "timestamp": "2024-07-06T00:00:00.000000",
                "workout_id": MOCK_WORKOUT_ID,
                "exercise_id": MOCK_EXERCISE_ID,
            }
        )
        MOCK_JOIN_ID = mock_join.generate_id()

        processes.post(ExerciseJoin, mock_user, mock_join)

        from_exercise = processes_module.exercise_join_filter(
            mock_user, exercise_id=MOCK_EXERCISE_ID
        )
        assert len(from_exercise) == 1
        assert isinstance(from_exercise[0], ExerciseJoin)
        assert from_exercise[0].object_id == MOCK_JOIN_ID

        from_workout = processes_module.exercise_join_filter(
            mock_user, workout_id=MOCK_WORKOUT_ID
        )
        assert len(from_workout) == 1
        assert isinstance(from_workout[0], ExerciseJoin)
        assert from_workout[0].object_id == MOCK_JOIN_ID

        from_both = processes_module.exercise_join_filter(
            mock_user,
            workout_id=MOCK_WORKOUT_ID,
            exercise_id=MOCK_EXERCISE_ID,
        )
        assert len(from_both) == 1
        assert isinstance(from_both[0], ExerciseJoin)
        assert from_both[0].object_id == MOCK_JOIN_ID

    def test_invalid_params(self, mock_user):
        with pytest.raises(
            ValueError,
            match="Invalid Usage: `exercise_join_filter` requires either `exercise_id` or `workout_id` or both, None provided",
        ):
            processes_module.exercise_join_filter(mock_user)


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestIdsFromExerciseJoins:

    def test_successful_conversion(self, mock_user):
        MOCK_EXERCISE_ID = uuid4()
        MOCK_WORKOUT_ID = uuid4()

        mock_join = ExerciseJoin.model_validate(
            {
                "user_id": MOCK_USER_ID,
                "timestamp": "2024-07-06T00:00:00.000000",
                "workout_id": MOCK_WORKOUT_ID,
                "exercise_id": MOCK_EXERCISE_ID,
            }
        )
        mock_join.generate_id()

        ids_dict = processes_module.ids_from_exercise_joins([mock_join])

        assert len(ids_dict["exercise_ids"]) == 1
        assert ids_dict["exercise_ids"][0] == MOCK_EXERCISE_ID

        assert len(ids_dict["workout_ids"]) == 1
        assert ids_dict["workout_ids"][0] == MOCK_WORKOUT_ID


@pytest.mark.usefixtures("env_vars", "set_up_aws_resources")
class TestTagJoinFilter:

    @pytest.mark.dependency(depends=["CREATE"])
    def test_successful_retrieval(self, mock_user, processes):
        MOCK_TAG_ID = uuid4()
        MOCK_TARGET_ID = uuid4()

        mock_join = TagJoin.model_validate(
            {
                "user_id": MOCK_USER_ID,
                "timestamp": "2024-07-06T00:00:00.000000",
                "target_id": MOCK_TARGET_ID,
                "target_object_type": ObjectType.WORKOUT.value,
                "tag_id": MOCK_TAG_ID,
            }
        )
        MOCK_JOIN_ID = mock_join.generate_id()

        processes.post(TagJoin, mock_user, mock_join)

        from_tag = processes_module.tag_join_filter(mock_user, tag_id=MOCK_TAG_ID)
        assert len(from_tag) == 1
        assert from_tag[0] == MOCK_JOIN_ID

        from_target = processes_module.tag_join_filter(
            mock_user, target_id=MOCK_TARGET_ID
        )
        assert len(from_target) == 1
        assert from_target[0] == MOCK_JOIN_ID

    def test_invalid_params(self, mock_user):
        with pytest.raises(
            ValueError,
            match="Invalid Usage: `tag_join_filter` requires either `tag_id` or `target_id`",
        ):
            processes_module.tag_join_filter(mock_user)

        with pytest.raises(
            ValueError,
            match="Invalid Usage: `tag_join_filter` requires either `tag_id` or `target_id`",
        ):
            processes_module.tag_join_filter(
                mock_user,
                tag_id=uuid4(),
                target_id=uuid4(),
            )
