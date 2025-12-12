# # # 1. Use Python 3.11 Slim as the base
# # FROM python:3.11-slim

# # # 2. Install 'uv' for fast package management
# # COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# # # 3. Set the working directory inside the container
# # WORKDIR /app

# # # 4. Copy dependency files first (Optimizes Docker caching)
# # COPY pyproject.toml uv.lock ./

# # # 5. Install dependencies
# # # --frozen: Fails if the lock file is out of sync (Safety Check)
# # # --no-dev: Skips dev tools like pytest (Saves Space)
# # # --system: Installs globally in the container (No need to activate venv)
# # RUN uv sync --frozen --no-dev --system

# # # 6. Copy the rest of the backend code
# # COPY . .

# # # 7. CRITICAL: Tell Python to look inside 'src' for modules
# # # This makes 'from agentic_travel_planner.worker import ...' work
# # ENV PYTHONPATH=/app/src

# # # 8. Default Command (FastAPI)
# # # Note: Docker Compose will override this for the 'worker' service
# # CMD ["uvicorn", "agentic_travel_planner.app:app", "--host", "0.0.0.0", "--port", "8000"]

# # 1. Use Python 3.11 Slim
# FROM python:3.11-slim

# # 2. Install 'uv'
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# # 3. Set working directory
# WORKDIR /app

# # 4. Copy dependency files
# COPY pyproject.toml uv.lock ./

# # --- FIX START ---
# # 5. Create the virtual environment and install dependencies
# # We removed '--system' and added the PATH variable below
# RUN uv sync --frozen --no-dev

# # 6. CRITICAL: Add the virtual environment to the PATH
# # This "activates" the venv for all future commands (like uvicorn/celery)
# ENV PATH="/app/.venv/bin:$PATH"
# # --- FIX END ---

# # 7. Copy the rest of the code
# COPY . .

# # 8. Tell Python where to find your src module
# ENV PYTHONPATH=/app/src

# # 9. Default Command
# CMD ["uvicorn", "agentic_travel_planner.app:app", "--host", "0.0.0.0", "--port", "8000"]
# 1. Use Python 3.11 Slim
FROM python:3.11-slim

# 2. Install 'uv'
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Set working directory
WORKDIR /app

# 4. Copy dependency files
COPY pyproject.toml uv.lock ./

# --- FIX IS HERE ---
# 5. Install dependencies ONLY (Ignore the project source code for now)
# We added '--no-install-project' to stop it from looking for 'src/'
RUN uv sync --frozen --no-dev --no-install-project

# 6. Add the virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# 7. Copy the rest of the code (NOW the src folder exists)
COPY . .

# 8. Tell Python where to find your src module
ENV PYTHONPATH=/app/src

# 9. Default Command
CMD ["uvicorn", "agentic_travel_planner.app:app", "--host", "0.0.0.0", "--port", "8000"]