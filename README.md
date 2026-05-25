# Fairway Forecast

A weather dashboard for golfers. Pick a Danish golf course from a dropdown, get a 24-hour weather forecast for that location, and receive AI-generated advice from a virtual caddie.

## How it works

1. On startup, the backend fetches all Danish golf courses from OpenStreetMap and keeps them in memory.
2. The user selects a course in the Streamlit UI and clicks **Get Forecast**.
3. The backend fetches a 24-hour hourly forecast from the Yr API (Norwegian Meteorological Institute) for that course's coordinates.
4. The forecast is passed to the Mistral AI API, which returns 2–3 sentences of practical golf advice.
5. The UI displays current conditions, a temperature/wind chart, and the AI caddie advice.

## Prerequisites

- Python 3.11+
- A [Mistral API key](https://console.mistral.ai/)
- Docker + Docker Compose (for the Docker option)

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_key_here
```

## Run locally (without Docker)

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend in one terminal:

```bash
cd backend && uvicorn main:app --reload --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend && streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Run with Docker

```bash
docker compose up --build
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Other commands

```bash
# Run tests
pytest tests/

# Type check
mypy backend/

# Lint
flake8 backend/ frontend/
```

## Project structure

```
fairway-forecast/
├── backend/
│   ├── main.py       # FastAPI app — /clubs, /weather, /advice endpoints
│   ├── weather.py    # Fetches and parses Yr API forecast data
│   ├── location.py   # Fetches Danish golf clubs from Overpass/OpenStreetMap
│   └── llm.py        # Builds prompt and calls Mistral API
├── frontend/
│   └── app.py        # Streamlit UI
├── tests/
│   ├── test_weather.py
│   └── test_location.py
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── requirements.txt
```
