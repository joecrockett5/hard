from fastapi import APIRouter
from starlette.requests import Request

from hard.models import Workout
from hard.aws.dynamodb.base_object import PARTITION_TEMPLATE
from hard.aws.dynamodb import ObjectType
from hard.aws.interfaces.fastapi import request

router = APIRouter(prefix="/workouts")

# WORKOUT_PARTITION = PARTITION_TEMPLATE.format({"object_type": ObjectType.WORKOUT.value})


@router.get("/", response_model=list[Workout])
def list_workouts(req: Request) -> list[Workout]:
    user = request.get_user_claims(req)
    pass


# @router.get("/{workout_id}", response_model=Workout)
# def get_workout(req: Request, workout_id: str) -> Workout:
#     user = request.get_user_claims(req)
#     pass


@router.post("/", response_model=Workout)
def create_workout(req: Request) -> Workout:
    user = request.get_user_claims(req)
    pass


@router.put("/{workout_id}", response_model=Workout)
def update_workout(req: Request, workout_id: str) -> Workout:
    user = request.get_user_claims(req)
    pass


@router.delete("/{workout_id}", response_model=Workout)
def delete_workout(req: Request, workout_id: str) -> Workout:
    user = request.get_user_claims(req)
    pass


@router.get("/test")
def test_endpoint():
    return {"message": "test-endpoint"}
