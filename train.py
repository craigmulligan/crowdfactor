import logging
from lib.app import app
from lib.train import train
from lib import worker

if __name__ == "__main__":
    with app.app_context():
        try:
            train()
        except Exception as e:
            logging.exception("Unexpected error running trainer")
