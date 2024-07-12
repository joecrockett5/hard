from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses
from hard.aws.dynamodb.consts import (
    ItemAccessUnauthorizedError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from hard.aws.interfaces.fastapi import request
from hard.models.tag import Tag

router = APIRouter(prefix="/tags")


@router.get("", response_model=list[Tag])
def list_tags(req: Request) -> list[Tag]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(Tag, user)


@router.get("/{tag_id}", response_model=Tag)
def get_tag(req: Request, tag_id: str):
    user = request.get_user_claims(req)
    try:
        tag = RestProcesses.get(Tag, user, UUID(tag_id))
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return tag


@router.post("", response_model=Tag)
def create_tag(req: Request, tag: Tag):
    user = request.get_user_claims(req)
    try:
        created_tag = RestProcesses.post(Tag, user, tag)
    except ItemAlreadyExistsError as err:
        return {"error": err}, 409
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return created_tag


@router.put("/{tag_id}", response_model=Tag)
def put(req: Request, tag_id: str, tag: Tag):
    user = request.get_user_claims(req)
    tag.object_id = UUID(tag_id)
    try:
        updated_tag = RestProcesses.put(Tag, user, tag)
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return updated_tag


@router.delete("/{tag_id}", response_model=Tag)
def delete(req: Request, tag_id: str):
    user = request.get_user_claims(req)
    try:
        deleted_tag = RestProcesses.delete(Tag, user, UUID(tag_id))
    except ItemNotFoundError as err:
        return {"error": err}, 404
    except ItemAccessUnauthorizedError as err:
        return {"error": err}, 401

    return deleted_tag
