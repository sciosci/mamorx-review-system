FROM python:3.11.10-slim-bookworm

# Poetry configs
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.4

RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gcc \
    cmake \
    python3-dev \
    pkg-config \
    libpoppler-cpp-dev \  
    libpoppler-dev \
    poppler-utils \
    libgl1-mesa-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.4

WORKDIR /app

COPY ./services/papermage_service/pyproject.toml ./services/papermage_service/poetry.lock /app/

RUN poetry install --only=main --no-root 

COPY ./MAMORX  /app/MAMORX

COPY ./config /app/config

COPY ./services/papermage_service /app/services/papermage_service

CMD ["poetry", "run", "python", "services/papermage_service/main.py"]