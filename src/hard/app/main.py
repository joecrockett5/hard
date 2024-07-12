from fastapi import APIRouter, FastAPI
from mangum import Mangum
from starlette.requests import Request

from hard.app.routes import exercises, sets, tags, workouts
from hard.aws.interfaces.fastapi import request
from hard.aws.models.user import User

api = APIRouter(prefix="/api")
api.include_router(workouts.router)
api.include_router(exercises.router)
api.include_router(sets.router)
api.include_router(tags.router)


@api.get("/user", response_model=User)
def get_user_claims(req: Request):
    return request.get_user_claims(req)


app = FastAPI()
app.include_router(api)

handler = Mangum(app)
