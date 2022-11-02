from urllib.parse import urlparse


def get_spot_id(surfline_url) -> str:
    """
    https://www.surfline.com/surf-report/venice-breakwater/590927576a2e4300134fbed8?camId=5834a1b6e411dc743a5d52f3
    """
    uri = urlparse(surfline_url)
    spot_id = uri.path.split("/")[3]
    return spot_id
