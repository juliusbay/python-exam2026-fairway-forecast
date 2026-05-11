# Fetches coordinates for a golf course name using OpenStreetMap Nominatim

import httpx
from typing import TypedDict


class LocationResult(TypedDict):
    name: str
    lat: float
    lon: float


# Returns up to 5 matching places for the given search query
def get_locations(query: str) -> list[LocationResult]:
    url = "https://nominatim.openstreetmap.org/search"
    params: dict[str, str | int] = {"q": query, "format": "json", "limit": 5}
    headers = {"User-Agent": "fairway-forecast/1.0"}

    response = httpx.get(url, params=params, headers=headers)
    response.raise_for_status()

    results = response.json()
    if not results:
        raise ValueError(f"No location found for: {query}")

    return [
        {
            "name": r["display_name"],
            "lat": float(r["lat"]),
            "lon": float(r["lon"]),
        }
        for r in results
    ]
