# Fetches Danish golf clubs from Overpass API on startup and stores them in memory

import httpx
from typing import TypedDict

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OVERPASS_QUERY = """
[out:json][timeout:25];
area["ISO3166-1"="DK"]->.denmark;
(
  way["leisure"="golf_course"](area.denmark);
  relation["leisure"="golf_course"](area.denmark);
);
out center;
"""


class LocationResult(TypedDict):
    name: str
    lat: float
    lon: float


# In-memory store populated at startup
DANISH_GOLF_CLUBS: list[LocationResult] = []


# Queries Overpass API and populates DANISH_GOLF_CLUBS; called once at server startup
async def fetch_danish_golf_clubs() -> None:
    headers = {"User-Agent": "fairway-forecast/1.0"}

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            OVERPASS_URL,
            data={"data": OVERPASS_QUERY},
            headers=headers,
        )
        response.raise_for_status()

    data = response.json()
    clubs: list[LocationResult] = []

    for element in data.get("elements", []):
        name: str | None = element.get("tags", {}).get("name")
        if not name:
            continue
        center = element.get("center", {})
        lat = center.get("lat")
        lon = center.get("lon")
        if lat is None or lon is None:
            continue
        clubs.append({"name": name, "lat": float(lat), "lon": float(lon)})

    clubs.sort(key=lambda c: c["name"])

    DANISH_GOLF_CLUBS.clear()
    DANISH_GOLF_CLUBS.extend(clubs)
