FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app

# Install deps
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project

# Copy code
COPY . .
RUN uv sync --frozen

CMD ["uv", "run", "python", "main.py"]