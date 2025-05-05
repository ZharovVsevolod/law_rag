# The builder image, used to build the virtual environment
FROM python:3.12-bookworm AS builder

RUN pip install poetry==2.1.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md
RUN poetry install --with api --no-root && rm -rf $POETRY_CACHE_DIR

COPY law_rag/ ./law_rag
RUN poetry install --only-root

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim-bookworm AS runtime

ENV VIRTUAL_ENV=/app/.venv \
PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY api_backend/api_activation.py ./
COPY law_rag/ ./law_rag
COPY config/ ./config
COPY data ./data
COPY .env ./.env

# Port may differ. See the config file `api.port`
EXPOSE 80 1702

# API
CMD ["python", "api_activation.py"]