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
docker compose up simulator app db
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
docker compose run --rm test uv run pytest -k test_dog_stays_within_boundary_over_long_simulation
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