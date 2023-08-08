from datetime import datetime, timedelta, timezone

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def local_timestamp(timestamp: datetime, offset: int) -> datetime:
    local_tz = timezone(timedelta(hours=offset))
    ts = timestamp.astimezone(local_tz)
    return ts


def datetime_to_string(dt: datetime) -> str:
    """
    Returns utc string for epoch
    """
    return dt.strftime(DATETIME_FORMAT)


def epoch_to_datetime(timestamp: int) -> datetime:
    """
    Returns utc string for epoch
    """
    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)


def str_to_timestamp(timestamp: str) -> datetime:
    """
    Returns utc datetime from string
    """
    return datetime.strptime(timestamp, DATETIME_FORMAT).replace(tzinfo=timezone.utc)


def str_to_local_timestamp(timestamp: str, offset: int) -> datetime:
    dt = str_to_timestamp(timestamp)
    return local_timestamp(dt, offset)
