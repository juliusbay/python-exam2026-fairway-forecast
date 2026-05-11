# Unit tests for location.py

import pytest
from unittest.mock import patch, MagicMock
from backend.location import get_locations


def make_response(json_data: list) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = json_data
    return mock


NOMINATIM_RESULTS = [
    {"display_name": "Augusta National Golf Club, Augusta, Georgia, US", "lat": "33.5006", "lon": "-82.0226"},
    {"display_name": "Augusta, Richmond County, Georgia, US", "lat": "33.4735", "lon": "-82.0105"},
]


def test_returns_list_of_results():
    with patch("backend.location.httpx.get", return_value=make_response(NOMINATIM_RESULTS)):
        results = get_locations("Augusta National")
    assert len(results) == 2


def test_parses_name_lat_lon():
    with patch("backend.location.httpx.get", return_value=make_response(NOMINATIM_RESULTS)):
        results = get_locations("Augusta National")
    assert results[0]["name"] == "Augusta National Golf Club, Augusta, Georgia, US"
    assert results[0]["lat"] == 33.5006
    assert results[0]["lon"] == -82.0226


def test_lat_lon_are_floats():
    with patch("backend.location.httpx.get", return_value=make_response(NOMINATIM_RESULTS)):
        results = get_locations("Augusta National")
    assert isinstance(results[0]["lat"], float)
    assert isinstance(results[0]["lon"], float)


def test_raises_on_empty_results():
    with patch("backend.location.httpx.get", return_value=make_response([])):
        with pytest.raises(ValueError, match="No location found"):
            get_locations("xkzqwerty")
