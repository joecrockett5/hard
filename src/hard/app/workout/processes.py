from hard.app.workout.routes import delete_workout
from hard.aws.dynamodb.consts import DB_PARTITION, PARTITION_TEMPLATE
from hard.aws.dynamodb.handler import Attr, Key, get_db_instance
from hard.aws.dynamodb.object_type import ObjectType
from hard.aws.models.user import User
from hard.models.workout import Workout


def list_workouts(user: User) -> list[Workout]:
    db = get_db_instance()
    query = db.query(
        key_expression=Key(DB_PARTITION).eq(
            PARTITION_TEMPLATE.format(
                **{
                    "user_id": user.id,
                    "object_type": ObjectType.WORKOUT.value,
                }
            )
        )
    )
    results = [Workout.from_db(item) for item in query]
    return results


def get_workout(workout_id: str) -> Workout:
    pass


def create_workout(workout: Workout) -> Workout:
    db = get_db_instance()

    result = db.put(data_object=workout)
    return result


def update_workout(updated_workout: Workout) -> Workout:
    pass


def delete_workout(workout_id: str) -> Workout:
    pass
