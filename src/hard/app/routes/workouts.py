from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses, workout_date_filter
from hard.aws.dynamodb.handler import get_db_instance
from hard.aws.interfaces.fastapi import request
from hard.models.exercise_join import ExerciseJoin
from hard.models.set import Set
from hard.models.workout import Workout

router = APIRouter(prefix="/workouts")


@router.get("", response_model=list[Workout])
async def list_workouts(
    req: Request,
    date: Optional[date] = None,
) -> list[Workout]:
    user = request.get_user_claims(req)

    if date:
        return workout_date_filter(user, date)

    return RestProcesses.get_list(Workout, user)


@router.get("/{workout_id}", response_model=Workout)
async def get_workout(
    req: Request,
    workout_id: str,
) -> Workout:
    user = request.get_user_claims(req)
    workout = RestProcesses.get(Workout, user, UUID(workout_id))

    return workout


@router.post("", response_model=Workout, status_code=201)
async def create_workout(
    req: Request,
    workout: Workout,
) -> Workout:
    user = request.get_user_claims(req)
    created_workout = RestProcesses.post(Workout, user, workout)

    return created_workout


@router.put("/{workout_id}", response_model=Workout)
async def update_workout(
    req: Request,
    workout_id: str,
    workout: Workout,
) -> Workout:
    user = request.get_user_claims(req)
    workout.object_id = UUID(workout_id)
    updated_workout = RestProcesses.put(Workout, user, workout)

    return updated_workout


@router.delete("/{workout_id}", response_model=Workout)
async def delete_workout(
    req: Request,
    workout_id: str,
) -> Workout:
    user = request.get_user_claims(req)
    db = get_db_instance()
    deleted_workout = RestProcesses.delete(Workout, user, UUID(workout_id))

    exercise_joins_to_delete = db.batch_get(
        user,
        target_object_cls=ExerciseJoin,
        search_attr="workout_id",
        matches_list=[workout_id],
    )

    sets_to_delete = db.batch_get(
        user,
        target_object_cls=Set,
        search_attr="exercise_join_id",
        matches_list=[join.object_id for join in exercise_joins_to_delete],
    )

    for join in exercise_joins_to_delete:
        RestProcesses.delete(ExerciseJoin, user, join.object_id)

    for set in sets_to_delete:
        RestProcesses.delete(Set, user, set.object_id)

    return deleted_workout
