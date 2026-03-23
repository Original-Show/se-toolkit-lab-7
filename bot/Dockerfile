ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy package requirements.
COPY pyproject.toml uv.lock ./

# Install dependencies in a frozen state so it strictly matches uv.lock
RUN uv sync --frozen --no-dev

# Copy the actual code.
COPY . .

# Run the bot entry point
CMD ["uv", "run", "bot.py"]
