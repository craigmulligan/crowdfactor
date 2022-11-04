from lib.camera import Camera
from lib.db import DB
from flask import current_app
from lib.utils import DATETIME_FORMAT
from datetime import datetime, timezone


def run():
    """
    This will get spot info from surfline API.
    Then setup a Camera to stream 60s of footage ./data
    Then cut the stream up into frames at $frame_rate using ffmpeg
    Then run the computer vision model to count the surfers in the water
    finally saving the lastest reading to the db.
    """
    ROBOFLOW_API_KEY = current_app.config.get("ROBOFLOW_API_KEY")
    ROBOFLOW_MODEL_VERSION = 2
    SURFLINE_SPOT_ID = current_app.config.get("SURFLINE_SPOT_ID")

    if ROBOFLOW_API_KEY is None:
        raise Exception(
            "Missing ROBOFLOW_API_KEY - make sure to set it as an environment variable"
        )

    if SURFLINE_SPOT_ID is None:
        raise Exception(
            "Missing SURFLINE_SPOT_ID - make sure to set it as an environment variable"
        )

    db = DB.get_db()
    # # ensure db schema
    db.setup()

    camera = Camera.get(SURFLINE_SPOT_ID, ROBOFLOW_API_KEY)

    # setup workspace
    # This cleans up any old files from previous runs.
    camera.workspace()

    # # # First save the 10s of live feed to video file
    camera.write_video()
    # # # # Them transform video to images
    camera.write_images()
    # Then analyze images.
    counters = camera.analyze(ROBOFLOW_MODEL_VERSION)
    crowd_count = camera.crowd_counter(counters)

    now = datetime.now().replace(tzinfo=timezone.utc)
    db.insert(
        crowd_count,
        camera.surf_rating,
        camera.spot_id,
        now.strftime(DATETIME_FORMAT),
        ROBOFLOW_MODEL_VERSION,
    )
    print(
        f"saved to db - crowd_count: {crowd_count}, surf_rating: {camera.surf_rating}"
    )
