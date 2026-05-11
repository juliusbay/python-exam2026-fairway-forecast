# Builds the prompt and calls the Mistral API to generate golf advice

import os
from dotenv import load_dotenv
from mistralai.client.sdk import Mistral
from mistralai.client.models.usermessage import UserMessage
from backend.weather import TimeSlot

load_dotenv()


# Summarises forecast slots into a short weather description for the prompt
def _summarise(slots: list[TimeSlot]) -> str:
    temps = [s["temperature"] for s in slots]
    wind_speeds = [s["wind_speed"] for s in slots]
    total_rain = sum(s["rain"] for s in slots)

    temp_range = f"{min(temps):.1f}–{max(temps):.1f}°C"
    avg_wind = f"{sum(wind_speeds) / len(wind_speeds):.1f} m/s"
    rain = f"{total_rain:.1f} mm" if total_rain > 0 else "no rain"

    return (
        f"Temperature: {temp_range}, average wind: {avg_wind}, "
        f"precipitation: {rain}"
    )


# Returns a short, friendly piece of golf advice based on the next 24h forecast
def get_advice(slots: list[TimeSlot]) -> str:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not set in environment")

    summary = _summarise(slots)
    prompt = (
        f"You are a friendly golf caddie. Based on today's weather forecast, "
        f"give a golfer 2–3 sentences of practical advice for their round. "
        f"Weather: {summary}."
    )

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[UserMessage(role="user", content=prompt)],  # type: ignore
    )

    if not response.choices or response.choices[0].message is None:
        return ""
    content = response.choices[0].message.content
    return content if isinstance(content, str) else ""
