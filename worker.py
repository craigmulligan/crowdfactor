import logging
from lib.app import app
from lib import worker
from lib import ml
from time import sleep
from lib.camera import CameraDownError, NightTimeError

if __name__ == "__main__":
    interval = 600

    with app.app_context():
        while True:
            try:
                worker.run()
            except NightTimeError as e:  
                logging.warning(e)
                logging.info("training model")
                try:
                    ml.train()
                except ml.NoTraingDataError: 
                    logging.debug("no new train data")
                except Exception as e:
                    logging.exception("Unexpected error training model")
            except (CameraDownError) as e:
                logging.warning(e)
            except Exception as e:
                logging.exception("Unexpected error running worker")

            sleep(interval)
