"""Работа с информацией о ТО (парсинг, формирование сообщений)"""
import re
from datetime import datetime

from app.db import get_last_maintenance, get_last_odo_on_car, get_service_interval
from app.utils import exceptions


def make_maintenance_info(user_id: str, car: str) -> str:
    """Создание сообщения с данными о последнем ТО и предстоящем ТО для определенного автомобиля"""
    try:
        last_maintenance = get_last_maintenance(user_id, car)
        if service_interval := get_service_interval(user_id):
            next_maintenance = last_maintenance.odo + service_interval
            last_odo = get_last_odo_on_car(user_id, car)
            until_next_maintenance = next_maintenance - last_odo
            if until_next_maintenance < 0:
                until_next_maintenance = f'ТО просрочено на <b>{abs(until_next_maintenance)} км</b>'
            else:
                until_next_maintenance = f'Следующее ТО через <b>{until_next_maintenance} км</b>'
        else:
            service_interval = until_next_maintenance = 'NOT FOUND'
        return f'Последнее ТО:\n\n' \
               f'🚗  <b>{car}</b>\n\n' \
               f'📅  {datetime.fromisoformat(last_maintenance.date).strftime("%d.%m.%Y")}\n\n' \
               f'📟  {last_maintenance.odo} км\n\n' \
               f'{until_next_maintenance}\n\n' \
               f'Установленный интервал {service_interval} км'
    except exceptions.NotFoundMaintenance as e:
        return str(e)


def parse_maintenance_date(text: str) -> str:
    """Парсит дату ТО"""
    regexp_result = re.fullmatch(r"\W*(\d{2})\W+(\d{2})\W+(\d{2})\W*", text)
    if not regexp_result or int(regexp_result.group(1)) > 31 or int(regexp_result.group(2)) > 12:
        raise exceptions.NotCorrectData("Некорректное значение! Введите дату в формате:\n\n<b>ДД.ММ.ГГ</b>")
    return f'20{regexp_result.group(3)}-{regexp_result.group(2)}-{regexp_result.group(1)}'


def parse_maintenance_number(text: str) -> int:
    """Парсит числа: пробег ТО, или интервал ТО"""
    regexp_result = re.fullmatch(r"\W*(\d+)\W*", text)
    if not regexp_result:
        raise exceptions.NotCorrectNumber("Некорректное значение! Попробуйте еще раз.")
    return int(regexp_result.group(1))
