from fastapi import APIRouter, FastAPI
from mangum import Mangum
from starlette.requests import Request

from hard.app import workout
from hard.aws.interfaces.fastapi import request
from hard.aws.models.user import User

api = APIRouter(prefix="/api")
api.include_router(workout.router)


@api.get("/user", response_model=User)
def get_user_claims(req: Request):
    return request.get_user_claims(req)


app = FastAPI()
app.include_router(api)

handler = Mangum(app)
