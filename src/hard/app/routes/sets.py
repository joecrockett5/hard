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
from hard.models.set import Set

router = APIRouter(prefix="/sets")


@router.get("", response_model=list[Set])
def list_sets(req: Request) -> list[Set]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(Set, user)


@router.get("/{set_id}", response_model=Set)
def get_set(req: Request, set_id: str):
    user = request.get_user_claims(req)
    try:
        set = RestProcesses.get(Set, user, UUID(set_id))
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return set


@router.post("", response_model=Set, status_code=201)
def create_set(req: Request, set: Set):
    user = request.get_user_claims(req)
    try:
        created_set = RestProcesses.post(Set, user, set)
    except ItemAlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return created_set


@router.put("/{set_id}", response_model=Set)
def put(req: Request, set_id: str, set: Set):
    user = request.get_user_claims(req)
    set.object_id = UUID(set_id)
    try:
        updated_set = RestProcesses.put(Set, user, set)
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return updated_set


@router.delete("/{set_id}", response_model=Set)
def delete(req: Request, set_id: str):
    user = request.get_user_claims(req)
    try:
        deleted_set = RestProcesses.delete(Set, user, UUID(set_id))
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return deleted_set
