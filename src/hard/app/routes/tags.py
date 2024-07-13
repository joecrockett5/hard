from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses, tags_from_target_id
from hard.aws.interfaces.fastapi import request
from hard.models.tag import Tag

router = APIRouter(prefix="/tags")


@router.get("", response_model=list[Tag])
async def list_tags(req: Request, target: Optional[UUID] = None) -> list[Tag]:
    user = request.get_user_claims(req)

    if target:
        return tags_from_target_id(user, target_id=target)

    return RestProcesses.get_list(Tag, user)


@router.get("/{tag_id}", response_model=Tag)
async def get_tag(
    req: Request,
    tag_id: str,
) -> Tag:
    user = request.get_user_claims(req)
    tag = RestProcesses.get(Tag, user, UUID(tag_id))

    return tag


@router.post("", response_model=Tag, status_code=201)
async def create_tag(
    req: Request,
    tag: Tag,
) -> Tag:
    user = request.get_user_claims(req)
    created_tag = RestProcesses.post(Tag, user, tag)

    return created_tag


@router.put("/{tag_id}", response_model=Tag)
async def update_tag(
    req: Request,
    tag_id: str,
    tag: Tag,
) -> Tag:
    user = request.get_user_claims(req)
    tag.object_id = UUID(tag_id)
    updated_tag = RestProcesses.put(Tag, user, tag)

    return updated_tag


@router.delete("/{tag_id}", response_model=Tag)
async def delete_tag(
    req: Request,
    tag_id: str,
) -> Tag:
    user = request.get_user_claims(req)
    deleted_tag = RestProcesses.delete(Tag, user, UUID(tag_id))

    return deleted_tag
