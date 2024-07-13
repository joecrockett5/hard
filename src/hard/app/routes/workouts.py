from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses
from hard.aws.interfaces.fastapi import request
from hard.models.workout import Workout

router = APIRouter(prefix="/workouts")


@router.get("", response_model=list[Workout])
async def list_workouts(
    req: Request,
) -> list[Workout]:
    user = request.get_user_claims(req)
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
    deleted_workout = RestProcesses.delete(Workout, user, UUID(workout_id))

    return deleted_workout
