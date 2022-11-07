import logging
from lib.app import app
from lib import worker
from time import sleep
from lib.camera import CameraDownError, NightTimeError

if __name__ == "__main__":
    with app.app_context():
        while True:
            try:
                worker.run()
            except (CameraDownError, NightTimeError) as e:
                # Valid errors
                logging.warning(e)
            except Exception as e:
                logging.exception("Unexpected error running worker")

            sleep(600)
