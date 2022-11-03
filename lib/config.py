# Custom object so we have config typing.
import os


class Config:
    ROBOFLOW_API_KEY: str
    SURFLINE_SPOT_ID: str
    DB_URL: str

    def __init__(self) -> None:
        ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")
        SURFLINE_SPOT_ID = os.environ.get("SURFLINE_SPOT_ID")
        DB_URL = os.environ.get("DB_URL", "data/crowdfactor.db")

        if ROBOFLOW_API_KEY is None:
            raise Exception(
                "Missing ROBOFLOW_API_KEY - make sure to set it as an environment variable"
            )

        if SURFLINE_SPOT_ID is None:
            raise Exception(
                "Missing SURFLINE_SPOT_ID - make sure to set it as an environment variable"
            )

        self.ROBOFLOW_API_KEY = ROBOFLOW_API_KEY
        self.SURFLINE_SPOT_ID = SURFLINE_SPOT_ID
        self.DB_URL = DB_URL
