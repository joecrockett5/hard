from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request

from hard.app.processes import RestProcesses
from hard.aws.interfaces.fastapi import request
from hard.models.template import Template

router = APIRouter(prefix="/templates")


@router.get("", response_model=list[Template])
async def list_templates(
    req: Request,
) -> list[Template]:
    user = request.get_user_claims(req)

    return RestProcesses.get_list(Template, user)


@router.get("/{template_id}", response_model=Template)
async def get_template(
    req: Request,
    template_id: str,
) -> Template:
    user = request.get_user_claims(req)
    template = RestProcesses.get(Template, user, UUID(template_id))

    return template


@router.post("", response_model=Template, status_code=201)
async def create_template(
    req: Request,
    template: Template,
) -> Template:
    user = request.get_user_claims(req)
    created_template = RestProcesses.post(Template, user, template)

    return created_template


@router.put("/{template_id}", response_model=Template)
async def update_template(
    req: Request,
    template_id: str,
    template: Template,
) -> Template:
    user = request.get_user_claims(req)
    template.object_id = UUID(template_id)
    updated_template = RestProcesses.put(Template, user, template)

    return updated_template


@router.delete("/{template_id}", response_model=Template)
async def delete_template(
    req: Request,
    template_id: str,
) -> Template:
    user = request.get_user_claims(req)
    deleted_template = RestProcesses.delete(Template, user, UUID(template_id))

    return deleted_template
