from fastapi import FastAPI
from mangum import Mangum

from hard.app import workout

app = FastAPI()
app.include_router(workout.router)

handler = Mangum(app)
