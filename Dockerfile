FROM balenalib/amd64-debian-python:3.11-bookworm

EXPOSE 8080

WORKDIR /home/user/app

# Note we have to manually add gnu-dbm. Because the balena images
# Don't include them see: https://github.com/docker-library/buildpack-deps/pull/49
RUN apt-get update && apt-get install ffmpeg -y && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

EXPOSE 8000
