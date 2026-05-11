# Streamlit UI — the only thing the user sees; calls the FastAPI backend

import os
import streamlit as st
import httpx
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Fairway Forecast")
st.caption("Weather forecasts and AI advice for your golf round.")

# --- Search bar ---
query = st.text_input(
    "Search for a golf course", placeholder="e.g. Augusta National Golf Club"
)
search = st.button("Search")

if search and query:
    res = httpx.get(f"{BACKEND}/location", params={"q": query})
    if res.status_code != 200 or not res.json():
        st.error("No results found. Try a different search.")
        st.stop()
    st.session_state["results"] = res.json()
    st.session_state["selected"] = None

# --- Result list ---
if st.session_state.get("results") and not st.session_state.get("selected"):
    st.write("Select a location:")
    for result in st.session_state["results"]:
        if st.button(result["name"], key=result["name"]):
            st.session_state["selected"] = result

# --- Dashboard ---
if st.session_state.get("selected"):
    location = st.session_state["selected"]

    with st.spinner("Fetching forecast..."):
        weather_res = httpx.get(
            f"{BACKEND}/weather",
            params={"lat": location["lat"], "lon": location["lon"]},
        )
        weather_res.raise_for_status()
        slots = weather_res.json()

        advice_res = httpx.post(
            f"{BACKEND}/advice", json={"slots": slots}, timeout=30
        )
        advice_res.raise_for_status()
        advice = advice_res.json()["advice"]

    # --- Location header ---
    st.subheader(location["name"])

    # --- Current conditions (first slot) ---
    now = slots[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperature", f"{now['temperature']} °C")
    c2.metric("Wind speed", f"{now['wind_speed']} m/s")
    c3.metric("Wind direction", f"{now['wind_direction']}°")
    c4.metric("Rain (next hour)", f"{now['rain']} mm")

    # --- Chart ---
    times = [datetime.fromisoformat(s["time"]) for s in slots]
    temps = [s["temperature"] for s in slots]
    winds = [s["wind_speed"] for s in slots]

    fig, ax1 = plt.subplots(figsize=(10, 4))

    ax1.set_xlabel("Time (UTC)")
    ax1.set_ylabel("Temperature (°C)", color="tab:red")
    ax1.plot(times, temps, color="tab:red", linewidth=2, label="Temperature")
    ax1.tick_params(axis="y", labelcolor="tab:red")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Wind speed (m/s)", color="tab:blue")
    ax2.plot(
        times, winds, color="tab:blue", linewidth=2,
        linestyle="--", label="Wind speed"
    )
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    fig.autofmt_xdate()

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.tight_layout()
    st.pyplot(fig)

    # --- AI advice ---
    st.divider()
    st.subheader("Caddie Advice")
    st.info(advice)
