from lib import utils
from datetime import datetime, timezone


def test_localtimestamp():
    ts = datetime.strptime("2022-11-03 14:31:27", utils.DATETIME_FORMAT).replace(
        tzinfo=timezone.utc
    )
    local_ts = utils.local_timestamp(ts, -7)
    assert local_ts.strftime(utils.DATETIME_FORMAT) == "2022-11-03 07:31:27"
