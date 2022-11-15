"""Работа с БД"""
import json

from utils import strtime

filename = 'db.json'


def set_new_data(new_data: dict) -> None:
    """Добавление нового объекта в БД"""
    data = get_data()
    data.update(new_data)
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


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


# def get_user_data(user_id) -> dict:
#     """Возвращает объект БД, связанный с пользователем
#     и удаляет его из БД"""
#     data = get_data()
#     return data[user_id]
