from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses
from hard.aws.interfaces.fastapi import request
from hard.models.tag_join import TagJoin

router = APIRouter(prefix="/tag-joins")


@router.get("", response_model=list[TagJoin])
async def list_tag_joins(
    req: Request,
) -> list[TagJoin]:
    user = request.get_user_claims(req)
    return RestProcesses.get_list(TagJoin, user)


@router.get("/{tag_join_id}", response_model=TagJoin)
async def get_tag_join(
    req: Request,
    tag_join_id: str,
) -> TagJoin:
    user = request.get_user_claims(req)
    tag_join = RestProcesses.get(TagJoin, user, UUID(tag_join_id))

    return tag_join


@router.post("", response_model=TagJoin, status_code=201)
async def create_tag_join(
    req: Request,
    tag_join: TagJoin,
) -> TagJoin:
    user = request.get_user_claims(req)
    created_tag_join = RestProcesses.post(TagJoin, user, tag_join)

    return created_tag_join


@router.put("/{tag_join_id}", response_model=TagJoin)
async def update_tag_join(
    req: Request,
    tag_join_id: str,
    tag_join: TagJoin,
) -> TagJoin:
    user = request.get_user_claims(req)
    tag_join.object_id = UUID(tag_join_id)
    updated_tag_join = RestProcesses.put(TagJoin, user, tag_join)

    return updated_tag_join


@router.delete("/{tag_join_id}", response_model=TagJoin)
async def delete_tag_join(
    req: Request,
    tag_join_id: str,
) -> TagJoin:
    user = request.get_user_claims(req)
    deleted_tag_join = RestProcesses.delete(TagJoin, user, UUID(tag_join_id))

    return deleted_tag_join
