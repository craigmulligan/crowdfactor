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
ROBOFLOW_API_KEY=<key> python worker.py https://www.surfline.com/surf-report/venice-breakwater/590927576a2e4300134fbed8\?camId\=5834a1b6e411dc743a5d52f3
```

### Running the server:

```
FLASK_DEBUG=1 FLASK_APP=lib/app flask run
```
