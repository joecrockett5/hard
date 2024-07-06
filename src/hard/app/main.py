from fastapi import FastAPI, APIRouter
from mangum import Mangum

from hard.app import workout

api = APIRouter(prefix="/api")
api.include_router(workout.router)

app = FastAPI()
app.include_router(api)

handler = Mangum(app)
