FROM python:3.12.7-slim-bookworm

# Poetry configs
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.4

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.4

WORKDIR /code

COPY ./services/mamorx_worker/pyproject.toml ./services/mamorx_worker/poetry.lock /code/

RUN poetry install --only=main --no-root 

COPY ./MAMORX  /code/MAMORX

COPY ./config /code/config

COPY ./services/mamorx_worker /code

CMD ["python", "app/main.py"]