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
from hard.models.exercise import Exercise

router = APIRouter(prefix="/exercises")


@router.get("", response_model=list[Exercise])
def list_exercises(req: Request) -> list[Exercise]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(Exercise, user)


@router.get("/{exercise_id}", response_model=Exercise)
def get_exercise(req: Request, exercise_id: str):
    user = request.get_user_claims(req)
    try:
        exercise = RestProcesses.get(Exercise, user, UUID(exercise_id))
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return exercise


@router.post("", response_model=Exercise)
def create_exercise(req: Request, exercise: Exercise):
    user = request.get_user_claims(req)
    try:
        created_exercise = RestProcesses.post(Exercise, user, exercise)
    except ItemAlreadyExistsError as err:
        return {"error": err}, 409
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return created_exercise


@router.put("/{exercise_id}", response_model=Exercise)
def put(req: Request, exercise_id: str, exercise: Exercise):
    user = request.get_user_claims(req)
    exercise.object_id = UUID(exercise_id)
    try:
        updated_exercise = RestProcesses.put(Exercise, user, exercise)
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return updated_exercise


@router.delete("/{exercise_id}", response_model=Exercise)
def delete(req: Request, exercise_id: str):
    user = request.get_user_claims(req)
    try:
        deleted_exercise = RestProcesses.delete(Exercise, user, UUID(exercise_id))
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return deleted_exercise
