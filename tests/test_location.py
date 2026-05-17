# Unit tests for location.py
# Tests the Overpass API initialization logic in fetch_danish_golf_clubs()

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from backend.location import DANISH_GOLF_CLUBS, fetch_danish_golf_clubs


# Builds a fake httpx async client that returns the given list of elements
def make_fake_client(elements: list) -> AsyncMock:
    # Fake the JSON body that Overpass API would return
    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.json.return_value = {"elements": elements}

    # Fake the client object used inside `async with httpx.AsyncClient() as client:`
    fake_client = AsyncMock()
    fake_client.post.return_value = fake_response
    return fake_client


# Runs fetch_danish_golf_clubs() with a fake client injected, so no real HTTP call is made
def run_with_fake_client(fake_client: AsyncMock) -> None:
    DANISH_GOLF_CLUBS.clear()
    with patch("backend.location.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__ = AsyncMock(return_value=fake_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=None)
        asyncio.run(fetch_danish_golf_clubs())


def test_parses_valid_golf_club():
    elements = [
        {
            "tags": {"name": "Rungsted Golf Klub"},
            "center": {"lat": 55.89, "lon": 12.54}
        }
    ]
    run_with_fake_client(make_fake_client(elements))

    # One valid club should have been added
    assert len(DANISH_GOLF_CLUBS) == 1
    # Name, lat, and lon should match the mock data exactly
    assert DANISH_GOLF_CLUBS[0]["name"] == "Rungsted Golf Klub"
    assert DANISH_GOLF_CLUBS[0]["lat"] == 55.89
    assert DANISH_GOLF_CLUBS[0]["lon"] == 12.54


def test_skips_club_if_wrong_country():
    elements = [
        {
            "tags": {"name": "Gothenburg Golf Club", "addr:country": "SE"},
            "center": {"lat": 57.7, "lon": 11.9}
        }
    ]
    run_with_fake_client(make_fake_client(elements))

    # A club tagged with a non-DK country should be filtered out
    assert len(DANISH_GOLF_CLUBS) == 0


def test_skips_club_if_missing_name_or_coordinates():
    elements = [
        # Missing the "name" tag entirely
        {
            "tags": {},
            "center": {"lat": 55.89, "lon": 12.54}
        },
        # Missing the "center" coordinates entirely
        {
            "tags": {"name": "Mystery Golf Klub"}
        }
    ]
    run_with_fake_client(make_fake_client(elements))

    # Neither bad element should crash the program or be added to the list
    assert len(DANISH_GOLF_CLUBS) == 0


def test_sorts_clubs_alphabetically():
    elements = [
        {
            "tags": {"name": "Zia Golf Klub"},
            "center": {"lat": 56.0, "lon": 10.0}
        },
        {
            "tags": {"name": "Aalborg Golf Klub"},
            "center": {"lat": 57.0, "lon": 9.9}
        }
    ]
    run_with_fake_client(make_fake_client(elements))

    # Aalborg should come before Zia even though Zia appeared first in the data
    assert DANISH_GOLF_CLUBS[0]["name"] == "Aalborg Golf Klub"
    assert DANISH_GOLF_CLUBS[1]["name"] == "Zia Golf Klub"
