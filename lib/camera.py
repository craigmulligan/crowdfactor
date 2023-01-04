import logging
import os
from typing import Optional, cast, Dict
import shutil
import glob
from urllib.parse import parse_qs
from collections import Counter

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


class Camera:
    id: str
    spot_id: str
    title: str
    url: str
    surf_rating: str
    roboflow_api_key: str
    frame_rate: int
    duration: int

    def __init__(
        self,
        id,
        title,
        url,
        spot_id,
        surf_rating,
        roboflow_api_key,
        frame_rate=25,
        duration=30,
    ):
        self.id = id
        self.title = title
        self.url = url
        self.surf_rating = surf_rating
        self.spot_id = spot_id
        self.frame_rate = frame_rate
        self.duration = duration
        self.roboflow_api_key = roboflow_api_key

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
        spot_rating = data["forecast"]["conditions"]["value"]
        logging.info(f"found: {spot_data['name']} - with current rating: {spot_rating}")

        # TODO improve error handling.
        if not len(spot_data["cameras"]):
            raise Exception("No Cam")

        camera = spot_data["cameras"][0]

        # Always just use the first one for now.
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
            camera["_id"],
            camera["title"],
            camera["streamUrl"],
            spot_data["_id"],
            spot_rating,
            roboflow_api_key,
        )
