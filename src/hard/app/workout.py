from fastapi import APIRouter

from hard.models import Workout

router = APIRouter(prefix="/workouts")


@router.get("/", response_model=list[Workout])
def list_workouts() -> list[Workout]:
    pass


@router.get("/{workout_id}", response_model=Workout)
def get_workout(workout_id: str) -> Workout:
    pass


@router.post("/", response_model=Workout)
def create_workout() -> Workout:
    pass


@router.put("/{workout_id}", response_model=Workout)
def update_workout(workout_id: str) -> Workout:
    pass


@router.delete("/{workout_id}", response_model=Workout)
def delete_workout(workout_id: str) -> Workout:
    pass
