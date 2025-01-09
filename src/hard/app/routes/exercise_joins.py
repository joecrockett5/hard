from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from hard.app.processes import RestProcesses, exercise_join_filter
from hard.aws.dynamodb.handler import get_db_instance
from hard.aws.interfaces.fastapi import request
from hard.models.exercise_join import ExerciseJoin
from hard.models.set import Set

router = APIRouter(prefix="/exercise-joins")


@router.get("", response_model=list[ExerciseJoin])
async def list_exercise_joins(
    req: Request,
    exercise: Optional[UUID] = None,
    workout: Optional[UUID] = None,
) -> list[ExerciseJoin] | ExerciseJoin:
    user = request.get_user_claims(req)
    if exercise or workout:
        relevant_joins = exercise_join_filter(user, exercise, workout)
        if len(relevant_joins) == 0:
            raise HTTPException(status_code=404, detail="No joins found")

        else:
            return relevant_joins
    else:
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
    db = get_db_instance()
    deleted_exercise_join = RestProcesses.delete(
        ExerciseJoin, user, UUID(exercise_join_id)
    )

    sets = db.batch_get(
        user,
        target_object_cls=Set,
        search_attr="exercise_join_id",
        matches_list=[exercise_join_id],
    )
    for set in sets:
        RestProcesses.delete(Set, user, set.object_id)

    return deleted_exercise_join


@router.delete("", response_model=ExerciseJoin)
async def delete_exercise_join_from_ids(
    req: Request,
    exercise: UUID,
    workout: UUID,
) -> ExerciseJoin:
    db = get_db_instance()
    user = request.get_user_claims(req)
    relevant_joins = exercise_join_filter(user, exercise, workout)
    if len(relevant_joins) == 0:
        raise HTTPException(status_code=404, detail="No joins found")
    elif len(relevant_joins) > 1:
        raise HTTPException(status_code=409, detail="Multiple joins found")
    else:
        to_delete = relevant_joins[0]
        deleted_exercise_join = RestProcesses.delete(
            ExerciseJoin, user, to_delete.object_id
        )

        sets = db.batch_get(
            user,
            target_object_cls=Set,
            search_attr="exercise_join_id",
            matches_list=[to_delete.object_id],
        )
        for set in sets:
            RestProcesses.delete(Set, user, set.object_id)

        return deleted_exercise_join
