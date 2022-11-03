FROM python:3.10

EXPOSE 8080

WORKDIR /home/user/app

RUN apt-get update && apt-get install ffmpeg cron -y && rm -rf /var/lib/apt/lists/*

RUN pip install --quiet --progress-bar off poetry==1.1.7

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

RUN echo "*/2 * * * * /usr/bin/python /home/user/app/worker.py > /dev/stdout" > /etc/cron.d/crowdfactor-crontab
RUN chmod 0644 /etc/cron.d/crowdfactor-crontab && crontab /etc/cron.d/crowdfactor-crontab
