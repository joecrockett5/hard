from typing import Optional, Type
from uuid import UUID

from hard.aws.dynamodb.base_object import CORE_ATTRIBUTES, DB_OBJECT_TYPE
from hard.aws.dynamodb.consts import (
    DB_PARTITION,
    DB_SORT_KEY,
    ITEM_INDEX_NAME,
    ITEM_INDEX_PARTITION,
    PARTITION_TEMPLATE,
    InvalidAttributeChangeError,
    ItemAccessUnauthorizedError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from hard.aws.dynamodb.handler import Attr, Key, get_db_instance
from hard.aws.dynamodb.object_type import ObjectType
from hard.aws.models.user import User
from hard.models.exercise import Exercise
from hard.models.exercise_join import ExerciseJoin
from hard.models.set import Set
from hard.models.tag_join import TagJoin


class RestProcesses:

    @staticmethod
    def get_list(
        object_cls: Type[DB_OBJECT_TYPE],
        user: User,
    ) -> list[DB_OBJECT_TYPE]:
        db = get_db_instance()

        query = db.query(
            key_expression=Key(DB_PARTITION).eq(
                PARTITION_TEMPLATE.format(
                    **{
                        "user_id": user.id,
                        "object_type": ObjectType.from_object_class(object_cls).value,
                    }
                )
            )
        )

        results = [object_cls.from_db(item) for item in query]
        return results

    @staticmethod
    def get(
        object_cls: Type[DB_OBJECT_TYPE],
        user: User,
        object_id: UUID,
    ) -> DB_OBJECT_TYPE:
        db = get_db_instance()

        query = db.query(
            secondary_index_name=ITEM_INDEX_NAME,
            key_expression=Key(ITEM_INDEX_PARTITION).eq(str(object_id)),
        )

        try:
            item = query[0]

        except IndexError:
            raise ItemNotFoundError(
                f"No `{ObjectType.from_object_class(object_cls).value}` found with `object_id`: '{object_id}'"
            )

        result = object_cls.from_db(item)

        if not result.owned_by(user):
            raise ItemAccessUnauthorizedError(
                f"`{ObjectType.from_object_class(object_cls).value}` Item not owned by current user ({user.id}): Cannot Fetch"
            )

        return result

    @staticmethod
    def post(
        object_cls: Type[DB_OBJECT_TYPE],
        user: User,
        data_object: DB_OBJECT_TYPE,
    ) -> DB_OBJECT_TYPE:
        db = get_db_instance()

        object_id = data_object.object_id or data_object.generate_id()

        try:
            RestProcesses.get(object_cls, user, object_id)

        except ItemNotFoundError:
            if not data_object.owned_by(user):
                raise ItemAccessUnauthorizedError(
                    f"`{ObjectType.from_object_class(object_cls).value}` Item not owned by current user ({user.id}): Cannot Create"
                )
            result = db.put(data_object=data_object)
            return result

        else:
            raise ItemAlreadyExistsError(
                f"Found `{ObjectType.from_object_class(object_cls).value}` with `object_id`: '{data_object.object_id}': Cannot Create"
            )

    @staticmethod
    def put(
        object_cls: Type[DB_OBJECT_TYPE],
        user: User,
        updated_object: DB_OBJECT_TYPE,
    ) -> DB_OBJECT_TYPE:
        db = get_db_instance()

        if not updated_object.owned_by(user):
            raise ItemAccessUnauthorizedError(
                f"`{ObjectType.from_object_class(object_cls).value}` Item not owned by current user ({user.id}): Cannot Update"
            )

        if not updated_object.object_id:
            raise ReferenceError(
                f"`{updated_object.object_type.value}` Item does not have a valid `object_id`"
            )

        try:
            current_obj = RestProcesses.get(object_cls, user, updated_object.object_id)

        except ItemNotFoundError:
            raise ItemNotFoundError(
                f"No `{ObjectType.from_object_class(object_cls).value}` found with `object_id`: '{updated_object.object_id}': Cannot Update"
            )

        for attr in CORE_ATTRIBUTES:
            if current_obj.__dict__[attr] != updated_object.__dict__[attr]:
                raise InvalidAttributeChangeError(
                    f"Cannot Modify `{attr}` Attribute on `{current_obj.object_type.value}`"
                )

        result = db.put(data_object=updated_object)
        return result

    @staticmethod
    def delete(
        object_cls: Type[DB_OBJECT_TYPE],
        user: User,
        object_id: UUID,
    ) -> DB_OBJECT_TYPE:
        db = get_db_instance()

        try:
            to_delete = RestProcesses.get(object_cls, user, object_id)

        except ItemNotFoundError:
            raise ItemNotFoundError(
                f"No `{ObjectType.from_object_class(object_cls).value}` found with `object_id`: '{object_id}': Cannot Delete"
            )

        except ItemAccessUnauthorizedError:
            raise ItemAccessUnauthorizedError(
                f"`{ObjectType.from_object_class(object_cls).value}` Item not owned by current user ({user.id}): Cannot Delete"
            )

        return db.delete(to_delete)


def exercise_join_filter(
    user: User,
    /,
    exercise_id: Optional[UUID] = None,
    workout_id: Optional[UUID] = None,
) -> list[ExerciseJoin]:
    if not (exercise_id or workout_id):
        raise ValueError(
            "Invalid Usage: `exercise_join_filter` requires either `exercise_id` or `workout_id` or both, None provided"
        )

    db = get_db_instance()

    partition = PARTITION_TEMPLATE.format(
        **{
            "user_id": user.id,
            "object_type": ObjectType.EXCERCISE_JOIN.value,
        }
    )

    filter = None
    if exercise_id:
        filter = Attr("exercise_id").eq(str(exercise_id))
    if workout_id:
        workout_filter = Attr("workout_id").eq(str(workout_id))
        filter = filter & workout_filter if filter else workout_filter

    json_items = db.query(
        key_expression=Key(DB_PARTITION).eq(partition),
        filter_expression=filter,
    )
    joins = [ExerciseJoin.from_db(item) for item in json_items]

    return joins


def ids_from_exercise_joins(joins: list[ExerciseJoin]) -> dict[str, list[UUID]]:
    out_dict = {
        "exercise_ids": [],
        "workout_ids": [],
    }

    for join in joins:
        out_dict["exercise_ids"].append(join.exercise_id)
        out_dict["workout_ids"].append(join.workout_id)

    return out_dict


def exercises_from_workout_id(user: User, workout_id: UUID) -> list[Exercise]:
    db = get_db_instance()

    joins = exercise_join_filter(user, workout_id=workout_id)
    ids = ids_from_exercise_joins(joins)

    exercises = db.batch_get(
        user,
        target_object_cls=Exercise,
        search_attr="object_id",
        matches_list=[str(id) for id in ids["exercise_ids"]],
    )
    return exercises


def sets_from_ids(
    user: User, /, workout_id: Optional[UUID] = None, exercise_id: Optional[UUID] = None
) -> list[Set]:
    db = get_db_instance()

    joins = exercise_join_filter(
        user,
        workout_id=workout_id,
        exercise_id=exercise_id,
    )
    join_ids = [str(join.object_id) for join in joins]

    sets = db.batch_get(
        user,
        target_object_cls=Set,
        search_attr="exercise_join_id",
        matches_list=join_ids,
    )
    return sets


def tag_join_filter(
    user: User,
    /,
    tag_id: Optional[UUID] = None,
    target_id: Optional[UUID] = None,
) -> list[UUID]:
    if bool(tag_id) == bool(target_id):
        raise ValueError(
            "Invalid Usage: `tag_join_filter` requires either `tag_id` or `target_id`"
        )

    db = get_db_instance()

    partition = PARTITION_TEMPLATE.format(
        **{
            "user_id": user.id,
            "object_type": ObjectType.TAG_JOIN.value,
        }
    )

    filter = None
    if tag_id:
        filter = Attr("tag_id").eq(str(tag_id))
    if target_id:
        filter = Attr("target_id").eq(str(target_id))

    json_items = db.query(
        key_expression=Key(DB_PARTITION).eq(partition),
        filter_expression=filter,
    )
    joins = [TagJoin.from_db(item) for item in json_items]

    ids = []
    for join in joins:
        if join.object_id is None:
            raise ValueError("Found `TagJoin` with NULL `object_id`")

        ids.append(join.object_id)

    return ids
