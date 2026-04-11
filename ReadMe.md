# First Run

Install dependencies
```bash
uv pip install .
```

Run the app
```bash
docker compose up app
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

# Useful commands

Install pre-commit on initial run 
```bash
uv run pre-commit install
```

See allowed commit msg formats - to see options stage a file
```bash
uv run cz commit
```