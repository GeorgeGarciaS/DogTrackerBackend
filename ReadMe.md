# Pet Telemetry Platform
A real-time telemetry ingestion and validation pipeline for tracking dog movement, with a simulator and frontend visualization.

### What it demonstrates
- Event ingestion pipeline (FastAPI)
- Data quality validation and routing
- Real-time state vs raw data separation
- dbt analytics layer (signal quality zones)
- PySpark decoupled processing (scalable architecture)

### Tech stack
FastAPI • Postgres • dbt • PySpark • Streamlit • Docker

### More information
https://docs.google.com/document/d/e/2PACX-1vQ1OyXJTvSxfrOJgDd0IeLu8g85qfq1Yq6f39XBgy7NvfipXXFKa2gwX9N_jWvIbGBear4G9qPzSmI8/pub


# Architecture Evolution

### Phase 1 — Ingestion Pipeline
- API validates and routes telemetry
- Stores raw, clean, rejected, and current state
- App frontend consumes /dog_current_status
- simulator logs dog tracker data to /telemetry

### Phase 2 — Analytics Layer (dbt , Pyspark)
- Aggregates telemetry into spatial signal zones
- Visualizes good vs bad signal areas
- Moves validation out of API to Pyspark for scalability
- Enables replay, scaling, and cleaner architecture




# First Run
Install dependencies
```bash
uv pip install .
```

### Backend with db (src)
Run the app
```bash
docker compose up app
```

### Simulator
Run the app
```bash
docker compose up simulator
```

### Frontend
Run the app
```bash
docker compose up frontend
```

# Linting

Run linting
```bash
docker compose run --rm lint
```

# Tests

Run all tests
```bash
docker compose run --rm test
```

Run one test suit by keyword
```bash
docker compose run --rm test uv run pytest -k < test_suite >
```

# Swagger

Swagger is configured to run in `http://localhost:8000/docs`

# Useful commands

Install pre-commit on initial run 
```bash
uv run pre-commit install
```

See allowed commit msg formats - to see options stage a file
```bash
uv run cz commit
```