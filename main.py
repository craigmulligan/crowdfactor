import os
import sys
from lib.camera import Camera
from lib.db import DB

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception(
            "a <url> is required eg: https://www.surfline.com/surf-report/venice-breakwater/590927576a2e4300134fbed8"
        )

    ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")

    if ROBOFLOW_API_KEY is None:
        raise Exception(
            "Missing ROBOFLOW_API_KEY - make sure to set it as an environment variable"
        )

    url = sys.argv[1]

    db = DB("./thelocal.db")
    # ensure db schema
    db.setup()

    camera = Camera.get_from_url(url, ROBOFLOW_API_KEY)
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

    db.insert(crowd_count, camera.surf_rating)
    print(
        f"saved to db - crowd_count: {crowd_count}, surf_rating: {camera.surf_rating}"
    )
