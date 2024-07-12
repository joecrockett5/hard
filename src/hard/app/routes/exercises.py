from uuid import UUID

from fastapi import APIRouter, HTTPException
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
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return exercise


@router.post("", response_model=Exercise, status_code=201)
def create_exercise(req: Request, exercise: Exercise):
    user = request.get_user_claims(req)
    try:
        created_exercise = RestProcesses.post(Exercise, user, exercise)
    except ItemAlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return created_exercise


@router.put("/{exercise_id}", response_model=Exercise)
def put(req: Request, exercise_id: str, exercise: Exercise):
    user = request.get_user_claims(req)
    exercise.object_id = UUID(exercise_id)
    try:
        updated_exercise = RestProcesses.put(Exercise, user, exercise)
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return updated_exercise


@router.delete("/{exercise_id}", response_model=Exercise)
def delete(req: Request, exercise_id: str):
    user = request.get_user_claims(req)
    try:
        deleted_exercise = RestProcesses.delete(Exercise, user, UUID(exercise_id))
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return deleted_exercise
