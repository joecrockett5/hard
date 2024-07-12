from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses
from hard.aws.dynamodb.consts import (
    ItemAccessUnauthorizedError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from hard.aws.interfaces.fastapi import request
from hard.models.workout import Workout

router = APIRouter(prefix="/workouts")


@router.get("", response_model=list[Workout])
def list_workouts(req: Request) -> list[Workout]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(Workout, user)


@router.get("/{workout_id}", response_model=Workout)
def get_workout(req: Request, workout_id: str):
    user = request.get_user_claims(req)
    try:
        workout = RestProcesses.get(Workout, user, UUID(workout_id))
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return workout


@router.post("", response_model=Workout)
def create_workout(req: Request, workout: Workout):
    user = request.get_user_claims(req)
    try:
        created_workout = RestProcesses.post(Workout, user, workout)
    except ItemAlreadyExistsError as err:
        return {"error": err}, 409
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return created_workout


@router.put("/{workout_id}", response_model=Workout)
def put(req: Request, workout_id: str, workout: Workout):
    user = request.get_user_claims(req)
    workout.object_id = UUID(workout_id)
    try:
        updated_workout = RestProcesses.put(Workout, user, workout)
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return updated_workout


@router.delete("/{workout_id}", response_model=Workout)
def delete(req: Request, workout_id: str):
    user = request.get_user_claims(req)
    try:
        deleted_workout = RestProcesses.delete(Workout, user, UUID(workout_id))
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return deleted_workout
