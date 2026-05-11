# Unit tests for weather.py

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from backend.weather import get_forecast


def make_entry(offset_hours: int, temp: float, wind: float, direction: float, rain: float) -> dict:
    time = datetime.now(timezone.utc) + timedelta(hours=offset_hours)
    return {
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {
            "instant": {"details": {
                "air_temperature": temp,
                "wind_speed": wind,
                "wind_from_direction": direction,
            }},
            "next_1_hours": {"details": {"precipitation_amount": rain}},
        },
    }


def make_response(entries: list) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = {"properties": {"timeseries": entries}}
    return mock


def test_returns_slots_within_24_hours():
    entries = [make_entry(i, temp=20.0, wind=5.0, direction=180.0, rain=0.0) for i in range(1, 30)]
    with patch("backend.weather.httpx.get", return_value=make_response(entries)):
        slots = get_forecast(55.0, 12.0)
    assert all(1 <= i <= 24 for i in range(1, len(slots) + 1))
    assert len(slots) == 24


def test_excludes_entries_outside_24_hours():
    entries = [
        make_entry(1, temp=20.0, wind=5.0, direction=180.0, rain=0.0),
        make_entry(25, temp=20.0, wind=5.0, direction=180.0, rain=0.0),
    ]
    with patch("backend.weather.httpx.get", return_value=make_response(entries)):
        slots = get_forecast(55.0, 12.0)
    assert len(slots) == 1


def test_parses_slot_fields_correctly():
    entries = [make_entry(1, temp=18.5, wind=3.2, direction=270.0, rain=1.4)]
    with patch("backend.weather.httpx.get", return_value=make_response(entries)):
        slots = get_forecast(55.0, 12.0)
    slot = slots[0]
    assert slot["temperature"] == 18.5
    assert slot["wind_speed"] == 3.2
    assert slot["wind_direction"] == 270.0
    assert slot["rain"] == 1.4


def test_rain_defaults_to_zero_when_missing():
    entry = make_entry(1, temp=20.0, wind=5.0, direction=90.0, rain=0.0)
    del entry["data"]["next_1_hours"]
    with patch("backend.weather.httpx.get", return_value=make_response([entry])):
        slots = get_forecast(55.0, 12.0)
    assert slots[0]["rain"] == 0.0


def test_excludes_past_entries():
    entries = [
        make_entry(-2, temp=20.0, wind=5.0, direction=180.0, rain=0.0),
        make_entry(1, temp=22.0, wind=4.0, direction=180.0, rain=0.0),
    ]
    with patch("backend.weather.httpx.get", return_value=make_response(entries)):
        slots = get_forecast(55.0, 12.0)
    assert len(slots) == 1
    assert slots[0]["temperature"] == 22.0
