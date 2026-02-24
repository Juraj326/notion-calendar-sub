FROM python:3.14-slim

# Create user first
RUN useradd -m appuser

WORKDIR /src

# Change ownership of workdir
RUN chown appuser:appuser /src

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Switch to appuser BEFORE everything else
USER appuser

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install dependencies (now .venv is owned by appuser)
RUN uv sync --frozen --no-dev

# Copy application code
COPY --chown=appuser:appuser app/ ./app/

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]