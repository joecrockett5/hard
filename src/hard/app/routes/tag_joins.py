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
from hard.models.tag_join import TagJoin

router = APIRouter(prefix="/tag_joins")


@router.get("", response_model=list[TagJoin])
def list_tag_joins(req: Request) -> list[TagJoin]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(TagJoin, user)


@router.get("/{tag_join_id}", response_model=TagJoin)
def get_tag_join(req: Request, tag_join_id: str):
    user = request.get_user_claims(req)
    try:
        tag_join = RestProcesses.get(TagJoin, user, UUID(tag_join_id))
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return tag_join


@router.post("", response_model=TagJoin, status_code=201)
def create_tag_join(req: Request, tag_join: TagJoin):
    user = request.get_user_claims(req)
    try:
        created_tag_join = RestProcesses.post(TagJoin, user, tag_join)
    except ItemAlreadyExistsError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return created_tag_join


@router.put("/{tag_join_id}", response_model=TagJoin)
def put(req: Request, tag_join_id: str, tag_join: TagJoin):
    user = request.get_user_claims(req)
    tag_join.object_id = UUID(tag_join_id)
    try:
        updated_tag_join = RestProcesses.put(TagJoin, user, tag_join)
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return updated_tag_join


@router.delete("/{tag_join_id}", response_model=TagJoin)
def delete(req: Request, tag_join_id: str):
    user = request.get_user_claims(req)
    try:
        deleted_tag_join = RestProcesses.delete(TagJoin, user, UUID(tag_join_id))
    except ItemNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except ItemAccessUnauthorizedError as err:
        raise HTTPException(status_code=401, detail=str(err))

    return deleted_tag_join
