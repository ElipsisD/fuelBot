from datetime import datetime

import pytz


def get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime:
    """Возвращает сегодняшний datetime с учётом временной зоны KJA."""
    tz = pytz.timezone("Asia/Krasnoyarsk")
    now = datetime.now(tz)
    return now
