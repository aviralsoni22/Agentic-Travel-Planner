FROM python:3.11-slim

# 2. Install 'uv'
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Set working directory
WORKDIR /app

# 4. Copy dependency files
COPY pyproject.toml uv.lock ./

# 5. Install dependencies ONLY (Ignore the project source code for now)
RUN uv sync --frozen --no-dev --no-install-project

# 6. Add the virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# 7. Copy the rest of the code (NOW the src folder exists)
COPY . .

# 8. Tell Python where to find your src module
ENV PYTHONPATH=/app/src

# 9. Default Command — honor $PORT (Render sets it; falls back to 8000 locally)
CMD ["sh", "-c", "uvicorn agentic_travel_planner.app:app --host 0.0.0.0 --port ${PORT:-8000}"]