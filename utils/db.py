"""Работа с БД"""
import json

from aiogram import types

from utils import strtime
from utils.exceptions import NotCorrectCarName

filename = 'db.json'


def set_data(data: dict) -> None:
    """Сохранение обновленной БД"""
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def get_data() -> dict:
    """Получение всей БД"""
    try:
        with open(filename, 'r', encoding='utf8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def new_user_check(user_id: str) -> bool:
    """Если user не в базе -> True;
    если user в базе -> False"""
    data = get_data()
    return not bool(data.get(user_id))


def new_refueling(user_id: str, car: str, odo: int, filing_volume: float) -> None:
    """Добавление данных о заправке конкретного пользователя"""
    data = get_data()
    new_ref = {'date': strtime.get_now_formatted(), 'car': car, 'odo': odo, 'filing_volume': filing_volume}
    data[user_id]['refuelings'].append(new_ref)
    set_data(data)


def user_cars(user_id: str) -> list:
    """Возвращает список автомобилей пользователя"""
    data = get_data()
    return data[user_id]['cars']


def get_last_odo_on_car(user_id: str, car: str) -> int:
    """Возвращает последний пробег на автомобиле либо 0"""
    for ref in get_data()[user_id]['refuelings'][::-1]:
        if ref['car'] == car and ref['odo'] != 0:
            return ref['odo']
    return 0


def get_two_last_ref_on_car(user_id: str, car: str) -> list:
    """Возвращает массив с информацией о 2-х последних заправках"""
    res = [ref for ref in get_data()[user_id]['refuelings'][::-1] if ref['car'] == car and ref['odo'] != 0]
    if len(res) >= 2:
        return res
    return []


def add_new_car(user_id: str, car: str) -> None:
    """Добавляет новый автомобиль пользователю, если такого еще не было"""
    db = get_data()
    if car not in db[user_id]['cars']:
        db[user_id]['cars'].append(car)
        set_data(db)
    else:
        raise NotCorrectCarName(
            'У тебя уже есть автомобиль с таким названием!\n'
            'Попробуй еще раз!'
        )


def delete_car(user_id: str, car: str) -> None:
    """Удаление автомобиля пользователя из базы"""
    db = get_data()
    db[user_id]['cars'].remove(car)
    set_data(db)


def set_new_data(m: types.Message) -> None:
    """Регистрация нового пользователя"""
    data = get_data()
    data.update({m.from_user.id: {
        'username': m.from_user.username,
        'first_name': m.from_user.first_name,
        'cars': [m.text],
        'refuelings': []
    }})
    set_data(data)
