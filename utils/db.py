"""Работа с БД"""
import datetime
import json
from pathlib import Path
from typing import NamedTuple

from aiogram import types

from utils import strtime, exceptions
from utils.exceptions import NotCorrectCarName


class Refueling(NamedTuple):
    date: str
    car: str
    odo: int | None
    filing_volume: float


class Maintenance(NamedTuple):
    date: str
    car: str
    odo: int


filename = 'db.json'
graph_path = 'fuelBot/users_graphs'


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
    new_ref = {
        'date': strtime.get_now_formatted(),
        'car': car,
        'odo': odo,
        'filing_volume': filing_volume}
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


def get_two_last_full_ref_on_car(user_id: str, car: str) -> list:
    """Возвращает массив с информацией о заправках между последними 2-мя полными заправками"""
    refuelings_iter = iter([ref for ref in get_data()[user_id]['refuelings'] if ref['car'] == car][::-1])
    res = []
    for ref in refuelings_iter:
        if ref['odo'] != 0:
            res.append(ref)
            break
    for ref in refuelings_iter:
        res.append(ref)
        if ref['odo'] != 0:
            return res
    return []


def get_last_partial_ref_on_car(user_id: str, car: str) -> list:
    """Возвращает массив с информацией о последних частичных заправках"""
    refuelings = [ref for ref in get_data()[user_id]['refuelings'] if ref['car'] == car]
    res = []
    for ref in refuelings[::-1]:
        if ref['odo'] != 0:
            return res
        res.append(ref)
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
        'refuelings': [],
        'maintenances': [],
    }})
    set_data(data)


def user_graph_check(user_id: str, car: str) -> bool | types.InputFile:
    """Проверяет есть ли созданный ранее график у пользователя"""
    p = Path(graph_path)
    if p.joinpath(f'{user_id}-{car}.png').exists():
        return types.InputFile(p.joinpath(f'{user_id}-{car}.png').as_posix())
    else:
        return False


def get_refuelings_list(user_id: str, car: str) -> list[Refueling]:
    """Возвращает список Refueling объектов для определенной машины пользователя"""
    return [Refueling(date=ref['date'], odo=ref['odo'], filing_volume=ref['filing_volume'], car=car)
            for ref in get_data()[user_id]['refuelings']
            if ref['car'] == car]


def get_service_interval(user_id: str) -> int:
    """Возвращает сервисный интервал пользователя, если его нет, то None"""
    return get_data()[user_id].get('service_interval')


def set_service_interval(user_id: str, interval: int) -> None:
    """Устанавливает сервисный интервал обслуживания автомобилей пользователя"""
    data = get_data()
    data[user_id]['service_interval'] = interval
    set_data(data)


def new_maintenance(user_id: str, info: Maintenance) -> None:
    """Добавление данных о новом ТО для определенной машины пользователя"""
    data = get_data()
    data[user_id]['maintenances'].append({
        'date': info.date,
        'car': info.car,
        'odo': info.odo,
    })
    set_data(data)


def get_last_maintenance(user_id: str, car: str) -> Maintenance:
    """Возвращает данные о последнем ТО для определенной машины пользователя"""
    try:
        last_maintenance = [i for i in get_data()[user_id]['maintenances'] if i['car'] == car][-1]
        return Maintenance(last_maintenance['date'], last_maintenance['car'], last_maintenance['odo'])
    except IndexError:
        raise exceptions.NotFoundMaintenance('Данные о ТО отсутствуют')


def get_refuelings_list_for_month(user_id: str, car: str) -> list[Refueling]:
    """Возвращает список Refueling объектов для определенной машины пользователя за последние 30 дней"""
    timedelta = datetime.datetime.today() - datetime.timedelta(days=30)
    return [
        Refueling(
            date=ref['date'],
            odo=ref['odo'],
            filing_volume=ref['filing_volume'],
            car=car
        )
        for ref in get_data()[user_id]['refuelings']
        if ref['car'] == car and datetime.datetime.fromisoformat(ref["date"]) >= timedelta
    ]


def get_refuelings_list_for_current_year(user_id: str, car: str) -> list[Refueling]:
    """Возвращает список Refueling объектов для определенной машины пользователя с начала текущего года"""
    today_year = datetime.datetime.today().year
    return [
        Refueling(
            date=ref['date'],
            odo=ref['odo'],
            filing_volume=ref['filing_volume'],
            car=car
        )
        for ref in get_data()[user_id]['refuelings']
        if ref['car'] == car and datetime.datetime.fromisoformat(ref["date"]).year >= today_year
    ]
