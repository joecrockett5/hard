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
from hard.models.exercise_join import ExerciseJoin

router = APIRouter(prefix="/exercise_joins")


@router.get("", response_model=list[ExerciseJoin])
def list_exercise_joins(req: Request) -> list[ExerciseJoin]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(ExerciseJoin, user)


@router.get("/{exercise_join_id}", response_model=ExerciseJoin)
def get_exercise_join(req: Request, exercise_join_id: str):
    user = request.get_user_claims(req)
    try:
        exercise_join = RestProcesses.get(ExerciseJoin, user, UUID(exercise_join_id))
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return exercise_join


@router.post("", response_model=ExerciseJoin, status_code=201)
def create_exercise_join(req: Request, exercise_join: ExerciseJoin):
    user = request.get_user_claims(req)
    try:
        created_exercise_join = RestProcesses.post(ExerciseJoin, user, exercise_join)
    except ItemAlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return created_exercise_join


@router.put("/{exercise_join_id}", response_model=ExerciseJoin)
def put(req: Request, exercise_join_id: str, exercise_join: ExerciseJoin):
    user = request.get_user_claims(req)
    exercise_join.object_id = UUID(exercise_join_id)
    try:
        updated_exercise_join = RestProcesses.put(ExerciseJoin, user, exercise_join)
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return updated_exercise_join


@router.delete("/{exercise_join_id}", response_model=ExerciseJoin)
def delete(req: Request, exercise_join_id: str):
    user = request.get_user_claims(req)
    try:
        deleted_exercise_join = RestProcesses.delete(
            ExerciseJoin, user, UUID(exercise_join_id)
        )
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return deleted_exercise_join
