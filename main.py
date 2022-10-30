import youtube_dl
import json
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Camera:
    title: str
    url: str


def get_video(camera: Camera):
    # Given cam url download the stream to a file.
    with youtube_dl.YoutubeDL({"max_downloads": 1, "no_playlist": True}) as ydl:
        ydl.download([camera.url])


def get_info(url):
    # Headers are needed otherwise surfline tries to bounce you.
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    page = requests.get(url, allow_redirects=True, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    content = soup.find("script", id="__NEXT_DATA__")
    assert content
    data = json.loads(content.text)
    spot_data = data["props"]["pageProps"]["ssrReduxState"]["spot"]["report"]["data"][
        "spot"
    ]
    print(f"found: {spot_data['name']}")
    print(f"with cameras:")

    if not len(spot_data["cameras"]):
        raise Exception("No Cam")

    # Always just use the first one for now.
    camera = spot_data["cameras"][0]

    if camera["status"]["isDown"]:
        raise Exception("Cam is down.")

    return Camera(camera["title"], camera["streamUrl"])


if __name__ == "__main__":
    # url = "https://www.surfline.com/surf-report/77th-st-rockaways/584204214e65fad6a7709d0a?camId=583498c9e411dc743a5d5288"
    # camera = get_info(url)
    get_video(
        Camera(
            "x", "https://cams.cdn-surfline.com/cdn-ec/ec-rockaway77th/playlist.m3u8"
        )
    )
