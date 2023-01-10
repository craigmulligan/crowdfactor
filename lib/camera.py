import logging
import os
from typing import Optional, cast, Dict
import shutil
import glob
from urllib.parse import parse_qs
from collections import Counter
from dataclasses import dataclass

# Third-party
import av
import ffmpeg
import requests
from roboflow import Roboflow

ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")


class NightTimeError(Exception):
    pass


class CameraDownError(Exception):
    pass

@dataclass
class Conditions:
    surf_rating: str 

    wind_speed: float 
    wind_gust: float 
    wind_direction: float 

    water_temp_max: float
    water_temp_min: float

    weather_temp: float
    weather_condition: str 

    wave_height_min: float
    wave_height_max: float


class Camera:
    id: str
    spot_id: str
    title: str
    url: str
    roboflow_api_key: str
    conditions: Conditions
    frame_rate: int
    duration: int


    def __init__(
        self,
        id,
        title,
        url,
        spot_id,
        roboflow_api_key,
        conditions,
        frame_rate=25,
        duration=30,
    ):
        self.id = id
        self.title = title
        self.url = url
        self.spot_id = spot_id
        self.frame_rate = frame_rate
        self.duration = duration
        self.roboflow_api_key = roboflow_api_key
        self.conditions = conditions

    @property
    def data_dir(self):
        return f"data/{self.id}"

    @property
    def video_file_name(self):
        return f"{self.data_dir}/output.mp4"

    def workspace(self):
        if os.path.isdir(self.data_dir):
            shutil.rmtree(self.data_dir)
            # if the demo_folder2 directory is
            # not present then create it.

        os.makedirs(self.data_dir)

    def write_video(self):
        # Given cam url download the stream to a file.
        if os.path.exists(self.video_file_name):
            os.remove(self.video_file_name)

        ffmpeg.input(self.url).trim(duration=self.duration).output(
            self.video_file_name
        ).run()

    def write_images(self):
        container = av.open(self.video_file_name)

        for i, frame in enumerate(container.decode(video=0)):
            if i % self.frame_rate == 0:
                frame.to_image().save(f"{self.data_dir}/frame-%04d.jpg" % frame.index)

    def analyze(self, model_version):
        rf = Roboflow(api_key=self.roboflow_api_key)
        project = rf.workspace().project("surfer-spotting")
        model = project.version(model_version).model
        assert model
        classes = ["surfer"]
        counters = []

        for filename in glob.glob(f"{self.data_dir}/*.jpg"):
            # checking if it is a file
            predictions = model.predict(filename, confidence=35, overlap=50)  # type: ignore

            if predictions is None:
                continue

            counter = Counter()

            for prediction in predictions:
                # For whatever reason typing thinks prediction is int.
                prediction = cast(Dict, prediction)

                if prediction["class"] in classes:
                    counter.update([prediction["class"]])

            counters.append(counter)

        return counters

    def crowd_counter(self, counters):
        """
        Because people can be obscured by frames we want to take the highest count
        over the period.
        """
        totals = [c.total() for c in counters]
        totals.sort(reverse=True)
        return totals[0]

    @staticmethod
    def get_camera_id(url: str) -> Optional[str]:
        qs = parse_qs(url)
        cam_id = qs.get("camId")

        if cam_id:
            return cam_id[0]

        return None

    @staticmethod
    def get(spot_id: str, roboflow_api_key: str, camera_id: Optional[str] = None):
        """
        Gets the camera stream url via spot URL.
        """
        res = requests.get(
            f"https://services.surfline.com/kbyg/spots/reports?spotId={spot_id}&corrected=false"
        )
        res.raise_for_status()
        data = res.json()
        spot_data = data["spot"]
        forecast = data["forecast"]

        conditions = Conditions(
            surf_rating = forecast["conditions"]["value"],
            wind_speed = forecast["wind"]["speed"],
            wind_gust = forecast["wind"]["gust"],
            wind_direction = forecast["wind"]["direction"],
            water_temp_max = forecast["waterTemp"]["max"] ,
            water_temp_min = forecast["waterTemp"]["min"] ,
            weather_temp = forecast["weather"]["temperature"] ,
            weather_condition = forecast["weather"]["condition"] ,
            wave_height_min = forecast["waveHeight"]["min"],
            wave_height_max = forecast["waveHeight"]["max"]
        )


        logging.info(f"found: {spot_data['name']} - with current rating: {conditions.surf_rating}")

        if not len(spot_data["cameras"]):
            raise Exception(f"Surf spot: {spot_id} does not have a camera.")

        # Default to the first one. 
        camera = spot_data["cameras"][0]

        if camera_id is not None:
            cameras = [
                camera for camera in spot_data["cameras"] if camera["_id"] == camera_id
            ]
            if len(cameras):
                raise Exception(f"Could not find camera {camera_id}")

            camera = cameras[0]

        if camera["status"]["isDown"]:
            raise CameraDownError("Cam is down.")

        if camera["nighttime"]:
            raise NightTimeError("Its night time.")

        return Camera(
            id=camera["_id"],
            title=camera["title"],
            url=camera["streamUrl"],
            spot_id=spot_data["_id"],
            roboflow_api_key=roboflow_api_key,
            conditions=conditions
        )
