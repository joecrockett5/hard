from fastapi import APIRouter, FastAPI, HTTPException, status
from mangum import Mangum
from starlette.requests import Request

from hard.app.routes import exercise_joins, exercises, sets, tag_joins, tags, workouts
from hard.aws.dynamodb.consts import (
    InvalidAttributeChangeError,
    ItemAccessUnauthorizedError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from hard.aws.interfaces.fastapi import request
from hard.aws.models.user import User

api = APIRouter(prefix="/api")
api.include_router(workouts.router)
api.include_router(exercises.router)
api.include_router(sets.router)
api.include_router(tags.router)
api.include_router(exercise_joins.router)
api.include_router(tag_joins.router)


@api.get("/user", response_model=User)
def get_user_claims(req: Request):
    return request.get_user_claims(req)


app = FastAPI()
app.include_router(api)


@app.exception_handler(InvalidAttributeChangeError)
async def invalid_attr_exc_handler(_req: Request, exc: InvalidAttributeChangeError):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.exception_handler(ItemAccessUnauthorizedError)
async def item_access_auth_exc_handler(_req: Request, exc: ItemAccessUnauthorizedError):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@app.exception_handler(ItemNotFoundError)
async def item_not_found_exc_handler(_req: Request, exc: ItemNotFoundError):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@app.exception_handler(ItemAlreadyExistsError)
async def item_already_exists_exc_handler(_req: Request, exc: ItemAlreadyExistsError):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


handler = Mangum(app)
