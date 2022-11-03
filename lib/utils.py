from datetime import datetime, timedelta, timezone

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def local_timestamp(timestamp: datetime, offset: int):
    local_tz = timezone(timedelta(hours=offset))
    return timestamp.replace(tzinfo=local_tz)
