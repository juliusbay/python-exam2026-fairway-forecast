# FastAPI app — defines all API endpoints (/clubs, /weather, /advice)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from backend.location import fetch_danish_golf_clubs, DANISH_GOLF_CLUBS
from backend.weather import get_forecast, TimeSlot
from backend.llm import get_advice


@asynccontextmanager
async def lifespan(app: FastAPI):
    await fetch_danish_golf_clubs()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/clubs")
def clubs():
    return DANISH_GOLF_CLUBS


@app.get("/weather")
def weather(lat: float, lon: float):
    return get_forecast(lat, lon)


class AdviceRequest(BaseModel):
    slots: list[TimeSlot]


@app.post("/advice")
def advice(body: AdviceRequest):
    return {"advice": get_advice(body.slots)}
