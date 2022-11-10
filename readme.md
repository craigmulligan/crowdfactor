# Crowd Factor 

## What is this

- TODO

## How it works

- TODO

## Usage:

```
poetry install
```

```
poetry shell
```

### Running the worker:

```
ROBOFLOW_API_KEY=<key> SURFLINE_URL=https://www.surfline.com/surf-report/venice-breakwater/590927576a2e4300134fbed8\?camId\=5834a1b6e411dc743a5d52f3 python worker.py
```

### Running the server :

```
FLASK_DEBUG=1 FLASK_APP=lib/app flask run
```

```
select avg(crowd_count) as avg_crowd_count, strftime('%H', timestamp) as hour, surf_rating, strftime('%w-%H', timestamp), timestamp 
from crowd_log
where strftime('%w-%H', timestamp) BETWEEN '3-00' AND '3-00'
group by strftime('%H', timestamp), surf_rating;
```
