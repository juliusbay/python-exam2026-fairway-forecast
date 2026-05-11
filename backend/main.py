# FastAPI app — defines all API endpoints (/location, /weather, /advice)

from fastapi import FastAPI
from pydantic import BaseModel
from backend.location import get_locations
from backend.weather import get_forecast, TimeSlot
from backend.llm import get_advice

app = FastAPI()


@app.get("/location")
def location(q: str):
    return get_locations(q)


@app.get("/weather")
def weather(lat: float, lon: float):
    return get_forecast(lat, lon)


class AdviceRequest(BaseModel):
    slots: list[TimeSlot]


@app.post("/advice")
def advice(body: AdviceRequest):
    return {"advice": get_advice(body.slots)}
