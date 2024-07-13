from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses, sets_from_ids
from hard.aws.interfaces.fastapi import request
from hard.models.set import Set

router = APIRouter(prefix="/sets")


@router.get("", response_model=list[Set])
async def list_sets(
    req: Request,
    workout_id: Optional[UUID] = None,
    exercise_id: Optional[UUID] = None,
) -> list[Set]:
    user = request.get_user_claims(req)

    if workout_id or exercise_id:
        return sets_from_ids(
            user,
            workout_id=workout_id,
            exercise_id=exercise_id,
        )

    return RestProcesses.get_list(Set, user)


@router.get("/{set_id}", response_model=Set)
async def get_set(
    req: Request,
    set_id: str,
) -> Set:
    user = request.get_user_claims(req)
    set = RestProcesses.get(Set, user, UUID(set_id))

    return set


@router.post("", response_model=Set, status_code=201)
async def create_set(
    req: Request,
    set: Set,
) -> Set:
    user = request.get_user_claims(req)
    created_set = RestProcesses.post(Set, user, set)

    return created_set


@router.put("/{set_id}", response_model=Set)
async def update_set(
    req: Request,
    set_id: str,
    set: Set,
) -> Set:
    user = request.get_user_claims(req)
    set.object_id = UUID(set_id)
    updated_set = RestProcesses.put(Set, user, set)

    return updated_set


@router.delete("/{set_id}", response_model=Set)
async def delete_set(
    req: Request,
    set_id: str,
) -> Set:
    user = request.get_user_claims(req)
    deleted_set = RestProcesses.delete(Set, user, UUID(set_id))

    return deleted_set
