from pathlib import Path

from aiogram.types import FSInputFile, Message

from app.db.service import service
from app.db.types import Maintenance, Refueling
from app.db.session import init_db

GRAPH_PATH = Path("users_graphs")


def new_user_check(user_id: str) -> bool:
    return service.new_user_check(user_id)


def set_new_user_data(user_id: str, username: str | None, first_name: str, car_name: str) -> None:
    service.set_new_user_data(user_id, username, first_name, car_name)


def set_new_data(message: Message) -> None:
    set_new_user_data(
        user_id=str(message.from_user.id),
        username=message.from_user.username,
        first_name=message.from_user.first_name or "",
        car_name=message.text,
    )


def new_refueling(user_id: str, car: str, odo: int, filing_volume: float) -> None:
    service.new_refueling(user_id, car, odo, filing_volume)


def user_cars(user_id: str) -> list[str]:
    return service.user_cars(user_id)


def get_last_odo_on_car(user_id: str, car: str) -> int:
    return service.get_last_odo_on_car(user_id, car)


def get_two_last_full_ref_on_car(user_id: str, car: str) -> list[dict]:
    return service.get_two_last_full_ref_on_car(user_id, car)


def get_last_user_refueling(user_id: str) -> Refueling | None:
    return service.get_last_user_refueling(user_id)


def change_last_refueling(user_id: str, odo: int, filing_volume: float) -> None:
    service.change_last_refueling(user_id, odo, filing_volume)


def get_last_partial_ref_on_car(user_id: str, car: str) -> list[dict]:
    return service.get_last_partial_ref_on_car(user_id, car)


def add_new_car(user_id: str, car: str) -> None:
    service.add_new_car(user_id, car)


def delete_car(user_id: str, car: str) -> None:
    service.delete_car(user_id, car)


def get_refuelings_list(user_id: str, car: str) -> list[Refueling]:
    return service.get_refuelings_list(user_id, car)


def get_service_interval(user_id: str) -> int | None:
    return service.get_service_interval(user_id)


def set_service_interval(user_id: str, interval: int) -> None:
    service.set_service_interval(user_id, interval)


def new_maintenance(user_id: str, info: Maintenance) -> None:
    service.new_maintenance(user_id, info)


def get_last_maintenance(user_id: str, car: str) -> Maintenance:
    return service.get_last_maintenance(user_id, car)


def get_refuelings_list_for_month(user_id: str, car: str) -> list[Refueling]:
    return service.get_refuelings_list_for_month(user_id, car)


def get_refuelings_list_for_current_year(user_id: str, car: str) -> list[Refueling]:
    return service.get_refuelings_list_for_current_year(user_id, car)


def user_graph_check(user_id: str, car: str) -> bool | FSInputFile:
    graph_file = GRAPH_PATH / f"{user_id}-{car}.png"
    return FSInputFile(graph_file.as_posix()) if graph_file.exists() else False

__all__ = [
    "Maintenance",
    "Refueling",
    "add_new_car",
    "change_last_refueling",
    "delete_car",
    "get_last_maintenance",
    "get_last_odo_on_car",
    "get_last_partial_ref_on_car",
    "get_last_user_refueling",
    "get_refuelings_list",
    "get_refuelings_list_for_current_year",
    "get_refuelings_list_for_month",
    "get_service_interval",
    "get_two_last_full_ref_on_car",
    "init_db",
    "new_maintenance",
    "new_refueling",
    "new_user_check",
    "service",
    "set_new_data",
    "set_new_user_data",
    "set_service_interval",
    "user_cars",
    "user_graph_check",
]
