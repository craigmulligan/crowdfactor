# Custom object so we have config typing.
import os


class Config:
    ROBOFLOW_API_KEY: str
    SURFLINE_SPOT_ID: str
    DB_URL: str

    def __init__(self) -> None:
        ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")
        SURFLINE_SPOT_ID = os.environ.get("SURFLINE_SPOT_ID", "")

        DB_URL = os.environ.get("DB_URL", "data/crowdfactor.db")
        MODEL_URL = os.environ.get("MODEL_URL", "data/model-v2")
        CACHE_URL = os.environ.get("CACHE_URL", "data/cache/")
        INTERVAL_CAMERA = int(os.environ.get("INTERVAL_CAMERA", "1200"))  # 20mins

        self.ROBOFLOW_API_KEY = ROBOFLOW_API_KEY
        self.SURFLINE_SPOT_ID = SURFLINE_SPOT_ID
        self.DB_URL = DB_URL
        self.MODEL_URL = MODEL_URL
        self.INTERVAL_CAMERA = INTERVAL_CAMERA
        self.INTERVAL_TRAINING = 86400  # 1 day
        self.CACHE_TYPE = "FileSystemCache"
        self.CACHE_DIR = CACHE_URL
        self.CACHE_DEFAULT_TIMEOUT = 300  # 5mins
