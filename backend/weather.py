# Fetches and parses forecast data from the Yr API

import httpx
from datetime import datetime, timezone, timedelta
from typing import TypedDict


class TimeSlot(TypedDict):
    time: str
    temperature: float
    wind_speed: float
    wind_direction: float
    rain: float


# Returns hourly forecast slots for the next 24 hours at the given coordinates
def get_forecast(lat: float, lon: float) -> list[TimeSlot]:
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    params = {"lat": round(lat, 4), "lon": round(lon, 4)}
    headers = {"User-Agent": "fairway-forecast/1.0"}

    response = httpx.get(url, params=params, headers=headers)
    response.raise_for_status()

    timeseries = response.json()["properties"]["timeseries"]

    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=24)

    slots: list[TimeSlot] = []
    for entry in timeseries:
        time = datetime.fromisoformat(entry["time"])
        if time < now or time > cutoff:
            continue

        details = entry["data"]["instant"]["details"]
        next_1h = entry["data"].get("next_1_hours", {}).get("details", {})

        slots.append({
            "time": entry["time"],
            "temperature": details["air_temperature"],
            "wind_speed": details["wind_speed"],
            "wind_direction": details["wind_from_direction"],
            "rain": next_1h.get("precipitation_amount", 0.0),
        })

    return slots
