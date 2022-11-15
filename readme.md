# Crowd Factor 

## What is this

As a surfer you are constantly trying to access the best time to surf. This not only involves looking at the forecast and conditions but also gauging when it's going to be most crowded - sometimes you'll get more waves if you surf when the conditions are a little worse but the spot is less crowded, a little game theory. In order to make the best decision on when to surf you need forecast data on both the waves conditions and the crowd. The former is easy to get from [surfline](https://www.surfline.com/) but there is no data on surf crowds, YET! 

## How it works

Crowdfactor will capture surf camera footage and use a computer vision model to count the number of surfers in the water. It then logs the surf conditions rating and the crowd count to a database. Once it has enough historical data it can can offer predictions of the crowd based on surf conditions and the time and day of the week. It serves these predictions on [webpage](https://9d6cb911e0cb153469c25e3e910ac831.balena-devices.com/). 


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

### Running the server:

```
FLASK_DEBUG=1 FLASK_APP=lib/app flask run
```

```
select avg(crowd_count) as avg_crowd_count, strftime('%H', timestamp) as hour, surf_rating, strftime('%w-%H', timestamp), timestamp 
from crowd_log
where strftime('%w-%H', timestamp) BETWEEN '3-00' AND '3-00'
group by strftime('%H', timestamp), surf_rating;
```
