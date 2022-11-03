FROM python:3.10

EXPOSE 8080

WORKDIR /home/user/app

RUN apt-get update && apt-get install ffmpeg cron -y && rm -rf /var/lib/apt/lists/*

RUN pip install --quiet --progress-bar off poetry==1.1.7

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

EXPOSE 8000
