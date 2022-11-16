"""Работа с данными о заправке"""
import re
from typing import NamedTuple

from aiogram import types

from utils import strtime
from . import db
from . import exceptions


class Refueling(NamedTuple):
    """Структура данных о новой заправке"""
    date: str
    car: str
    odo: int
    filing_volume: float
    # TODO оптимизировать код под использование класса Refueling


def add_refueling(message: types.Message, cars: list = None, selected_car: str = None):
    """Добавление новой заправки в БД"""
    user_id = str(message.from_user.id)
    odo, filing_volume = _parse_message(message.text)
    if cars:
        db.set_new_data({
            user_id: {
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'cars': cars,
                'refuelings': [
                    {
                        'date': strtime.get_now_formatted(),
                        'car': selected_car,
                        'odo': odo,
                        'filing_volume': filing_volume
                    }
                ]
            }
        })
    else:
        db.new_refueling(user_id, selected_car, odo, filing_volume)


def _parse_message(raw_message: str) -> tuple:
    """Парсит текст сообщения о новой заправке"""
    regexp_result = re.fullmatch(r"([\d.,]+)\s+(\d+)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectRefueling(
            "Не могу понять сообщение. Напишите сообщение в формате, например:"
            "\n23,54 68900")
    filing_volume = float(regexp_result.group(1).replace(',', '.'))
    odo = int(regexp_result.group(2))
    return odo, filing_volume
