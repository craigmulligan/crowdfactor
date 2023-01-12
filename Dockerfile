FROM balenalib/amd64-debian-python:3.11-bookworm

EXPOSE 8080

WORKDIR /home/user/app

RUN apt-get update && apt-get install ffmpeg -y && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

EXPOSE 8000
