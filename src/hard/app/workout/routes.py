from fastapi import APIRouter
from starlette.requests import Request

from hard.aws.dynamodb import ObjectType
from hard.aws.interfaces.fastapi import request
from hard.models import Workout

router = APIRouter(prefix="/workouts")

# WORKOUT_PARTITION = PARTITION_TEMPLATE.format({"object_type": ObjectType.WORKOUT.value})


@router.get("")
def list_workouts(req: Request) -> Workout:
    user = request.get_user_claims(req)
    return {"email": user.email}


@router.get("/{workout_id}", response_model=Workout)
def get_workout(req: Request, workout_id: str):
    user = request.get_user_claims(req)
    pass


@router.post("")
def create_workout(req: Request):
    user = request.get_user_claims(req)
    pass


@router.put("/{workout_id}")
def update_workout(req: Request, workout_id: str):
    user = request.get_user_claims(req)
    pass


@router.delete("/{workout_id}")
def delete_workout(req: Request, workout_id: str):
    user = request.get_user_claims(req)
    pass
