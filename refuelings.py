"""Работа с сообщениями о заправке"""
import re
import datetime
import pytz
from aiogram import types

import db
import exceptions


def add_refueling(message: types.Message):
    """Добавление нового расхода в БД.
    На вход принимает сообщение от пользователя"""
    user_id = message.from_user.id
    if new_user_check(user_id):
        pass
    else:
        for obj in db.get_data():
            if obj['user_id'] == user_id:
                """создать новый объект с добавлением данных о новой заправке
                обновить бд"""

                pass


def new_user_check(id: int) -> bool:
    """Проверяет есть ли пользователь в базе,
    если нет, возвращает True,
    если есть, то возвращает False"""
    data = db.get_data()
    for obj in data:
        if obj['user_id'] == id:
            return False
    return True


def _parse_message(raw_message: str) -> tuple:
    """Парсит текст пришедшего сообщения о новой заправке"""
    regexp_result = re.match(r"([\d.,]+)\s+(\d+)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectRefueling(
            "Не могу понять сообщение. Напишите сообщение в формате, например:"
            "\n23,54 68900")
    filing_volume = float(regexp_result.group(1).replace(',', '.'))
    odo = int(regexp_result.group(2))
    return filing_volume, odo


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом временной зоны KJA."""
    tz = pytz.timezone("Asia/Krasnoyarsk")
    now = datetime.datetime.now(tz)
    return now
