from datetime import datetime, timedelta, timezone

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def local_timestamp(timestamp: datetime, offset: int) -> datetime:
    local_tz = timezone(timedelta(hours=offset))
    ts = timestamp.astimezone(local_tz)
    return ts
