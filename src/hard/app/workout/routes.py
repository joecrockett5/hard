from fastapi import APIRouter
from starlette.requests import Request

from hard.app.workout import processes
from hard.aws.dynamodb.consts import ItemAlreadyExistsError, ItemNotFoundError
from hard.aws.interfaces.fastapi import request
from hard.models.workout import Workout

router = APIRouter(prefix="/workouts")

# WORKOUT_PARTITION = PARTITION_TEMPLATE.format({"object_type": ObjectType.WORKOUT.value})


@router.get("", response_model=list[Workout])
def get_list(req: Request) -> list[Workout]:
    user = request.get_user_claims(req)
    return processes.list_workouts(user)


@router.get("/{workout_id}", response_model=Workout)
def get(workout_id: str):
    try:
        workout = processes.get_workout(workout_id)
    except ItemNotFoundError as err:
        return {"error": err}, 404

    return workout


@router.post("", response_model=Workout)
def post(workout: Workout):
    try:
        processes.create_workout(workout)
    except ItemAlreadyExistsError as err:
        return {"error": err}, 409

    return workout


@router.put("/{workout_id}", response_model=Workout)
def put(workout_id: str, workout: Workout):
    if workout.object_id != workout_id:
        return {"error": "`Workout.object_id` cannot be changed"}, 400

    try:
        processes.update_workout(workout)
    except ItemNotFoundError as err:
        return {"error": err}, 404

    return workout


@router.delete("/{workout_id}", response_model=Workout)
def delete(workout_id: str):
    try:
        deleted_workout = processes.delete_workout(workout_id)
    except ItemNotFoundError as err:
        return {"error": err}, 404

    return deleted_workout
