from typing import NamedTuple


class Refueling(NamedTuple):
    date: str
    car: str
    odo: int | None
    filing_volume: float


class Maintenance(NamedTuple):
    date: str
    car: str
    odo: int
