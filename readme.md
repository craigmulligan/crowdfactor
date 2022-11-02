# The local 

> A surf cam crowd analyzer

Surf breaks, especially ones with cameras are typically crowded. Which means going for a surf at the optimal time is crucial if you want to get a few waves. You have to spend a lot of time getting a feel for when the water is likely to be crowed.

This project uses the surf camera stream and a computer vision model trained via roboflow to determine how many people are in the lineup, taking a 10 second sample every 10 minutes.

With this you could:

1. Get notified when it's a good time to surf.
2. Predict when it's going to be a good time to surf.


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

# TODO:

1. When loading page get most recent forecast for that day. With hourly ratings. Eg hour 0: rating.
2. Then get avg crowd count for each hour for each rating. Then combine this result with data from `1.`. *HOWEVER* this should only be for days in the future - anything in the past should just use the real values. 
