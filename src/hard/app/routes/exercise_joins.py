from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses
from hard.aws.interfaces.fastapi import request
from hard.models.exercise_join import ExerciseJoin

router = APIRouter(prefix="/exercise_joins")


@router.get("", response_model=list[ExerciseJoin])
async def list_exercise_joins(
    req: Request,
) -> list[ExerciseJoin]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(ExerciseJoin, user)


@router.get("/{exercise_join_id}", response_model=ExerciseJoin)
async def get_exercise_join(
    req: Request,
    exercise_join_id: str,
) -> ExerciseJoin:
    user = request.get_user_claims(req)
    exercise_join = RestProcesses.get(ExerciseJoin, user, UUID(exercise_join_id))

    return exercise_join


@router.post("", response_model=ExerciseJoin, status_code=201)
async def create_exercise_join(
    req: Request,
    exercise_join: ExerciseJoin,
) -> ExerciseJoin:
    user = request.get_user_claims(req)
    created_exercise_join = RestProcesses.post(ExerciseJoin, user, exercise_join)

    return created_exercise_join


@router.put("/{exercise_join_id}", response_model=ExerciseJoin)
async def update_exercise_join(
    req: Request,
    exercise_join_id: str,
    exercise_join: ExerciseJoin,
) -> ExerciseJoin:
    user = request.get_user_claims(req)
    exercise_join.object_id = UUID(exercise_join_id)
    updated_exercise_join = RestProcesses.put(ExerciseJoin, user, exercise_join)

    return updated_exercise_join


@router.delete("/{exercise_join_id}", response_model=ExerciseJoin)
async def delete_exercise_join(
    req: Request,
    exercise_join_id: str,
) -> ExerciseJoin:
    user = request.get_user_claims(req)
    deleted_exercise_join = RestProcesses.delete(
        ExerciseJoin, user, UUID(exercise_join_id)
    )

    return deleted_exercise_join
