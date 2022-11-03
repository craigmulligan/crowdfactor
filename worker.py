import os
import sys
from lib.camera import Camera, NightTimeError, CameraDownError
from lib.db import DB
from lib.app import app

if __name__ == "__main__":
    # Running in flask app
    # context ensures we cleanup db connections
    # etc.
    with app.app_context():
        ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")
        SURFLINE_SPOT_ID = os.environ.get("SURFLINE_SPOT_ID")

        if ROBOFLOW_API_KEY is None:
            raise Exception(
                "Missing ROBOFLOW_API_KEY - make sure to set it as an environment variable"
            )

        if SURFLINE_SPOT_ID is None:
            raise Exception(
                "Missing SURFLINE_SPOT_ID - make sure to set it as an environment variable"
            )

        db = DB.get_db()
        # ensure db schema
        db.setup()

        try:
            camera = Camera.get(SURFLINE_SPOT_ID, ROBOFLOW_API_KEY)
        except (CameraDownError, NightTimeError) as e:
            # Valid errors
            print(e)
            sys.exit(0)

        # setup workspace
        # This cleans up any old files from previous runs.
        camera.workspace()

        # # # First save the 10s of live feed to video file
        camera.write_video()
        # # # # Them transform video to images
        camera.write_images()
        # Then analyze images.
        counters = camera.analyze()
        crowd_count = camera.crowd_counter(counters)

        db.insert(crowd_count, camera.surf_rating, camera.spot_id)
        print(
            f"saved to db - crowd_count: {crowd_count}, surf_rating: {camera.surf_rating}"
        )
