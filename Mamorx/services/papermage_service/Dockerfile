FROM python:3.11.10-slim-bookworm

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
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.4

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install --no-dev --no-root 

COPY ./MAMORX  /app/

COPY ./config /app/

COPY ./services/papermage_service/figure_critic_server.py /app/

COPY ./services/papermage_service/main.py /app/

CMD ["python", "main.py"]