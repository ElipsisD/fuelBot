"""Работа с данными о заправке"""
import re
from datetime import datetime

from aiogram import types

from . import db
from . import exceptions
from .db import Refueling
from .graphs_settings import make_graph_stat


def add_refueling(message: types.Message, ref_mode: str, selected_car: str = None) -> None:
    """Добавление новой заправки в БД"""
    user_id = str(message.from_user.id)
    if ref_mode == 'full':
        odo, filing_volume = _parse_message(message.text)
        if last_ref := db.get_last_odo_on_car(user_id, selected_car):  # else первая заправка на этом автомобиле
            if last_ref > odo:
                raise exceptions.NotCorrectRefueling(
                    f'Пробег с последнего раза не увеличился!\n'
                    f'В прошлый раз было {last_ref} км\n'
                    f'Попробуй еще раз'
                )
    else:
        odo, filing_volume = 0, float(message.text.replace(',', '.').strip())
    db.new_refueling(user_id, selected_car, odo, filing_volume)


def _parse_message(raw_message: str) -> tuple:
    """Парсит текст сообщения о новой заправке"""
    regexp_result = re.fullmatch(r"([\d.,]+)\s+(\d+)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectRefueling(
            "Не могу понять сообщение. Напишите сообщение в формате, например:\n"
            "<b>23,54 68900</b>"
        )
    filing_volume = float(regexp_result.group(1).replace(',', '.'))
    odo = int(regexp_result.group(2))
    return odo, filing_volume


def last_fuel_expense(user_id: str, car: str) -> str:
    """Вычисление расхода за последний промежуток между полными заправками для отправки в результирующее сообщение"""
    if refs := db.get_two_last_full_ref_on_car(user_id, car):
        distance = refs[0]['odo'] - refs[-1]['odo']  # Пройденная дистанция
        spent_fuel = sum(i['filing_volume'] for i in refs[:-1])
        expense = round(spent_fuel / distance * 100, 2)  # Расход
        answer = f'🚗  {car}\n\n' \
                 f'📅  {datetime.fromisoformat(refs[0]["date"]).strftime("%d.%m.%Y %H:%M")}\n\n' \
                 f'📊  <b>{expense}</b> л / 100 км'
        if until := get_distance_to_maintenance(user_id, car):
            if 0 < until < 500:
                answer += '\n\n' + f'Следующее ТО через <b>{until} км</b>'
            elif until < 0:
                answer += '\n\n' + f'ТО просрочено на <b>{abs(until)} км</b>'
        return answer
    else:
        raise exceptions.NotEnoughRefuelings(
            'Для оценки расхода необходимо заправиться до полного бака минимум 2 раза 🗿')


def volume_since_last_full_fill(user_id: str, car: str) -> str:
    """Возвращает количество литров, заправленные с последней полной заправки"""
    refs = db.get_last_partial_ref_on_car(user_id, car)
    volume = round(sum(ref['filing_volume'] for ref in refs))
    return f'🚗  {car}\n\n' \
           f'📅  {datetime.fromisoformat(refs[0]["date"]).strftime("%d.%m.%Y %H:%M")}\n\n' \
           f'⛽  Заправил уже <b>{volume}</b> л'


def graph_stat(user_id: str, car: str) -> types.InputFile:
    """Проверяет есть ли график, если нет, то создает и возвращает InputPhoto"""
    if photo := db.user_graph_check(user_id, car):
        return photo
    else:
        return update_graph_stat(user_id, car)


def update_graph_stat(user_id: str, car: str) -> types.InputFile:
    """Создает график и возвращает InputPhoto"""
    expenses = _get_data_for_graph(user_id, car)
    return make_graph_stat(user_id, car, expenses)


def _get_data_for_graph(user_id: str, car: str) -> tuple:
    data_iter = iter(db.get_refuelings_list(user_id, car))
    expenses = ([], [])
    prev_odo = 0
    for ref in data_iter:
        if ref.odo != 0:
            prev_odo = ref.odo
            break
    volume_counter = 0
    for ref in data_iter:
        volume_counter += ref.filing_volume
        if ref.odo != 0:
            expense = round(volume_counter / (ref.odo - prev_odo) * 100, 2)
            expenses[0].append(expense)
            expenses[1].append(datetime.fromisoformat(ref.date))
            prev_odo = ref.odo
            volume_counter = 0
    if expenses[0]:
        return expenses
    else:
        raise exceptions.NotEnoughRefuelings(
            'Для оценки расхода необходимо заправиться до полного бака минимум 2 раза 🗿')


def get_distance_to_maintenance(user_id: str, car: str) -> int | None:
    """Вычисляет сколько осталось км до ТО на данном автомобиле пользователя"""
    try:
        last_maintenance = db.get_last_maintenance(user_id, car)
        if service_interval := db.get_service_interval(user_id):
            next_maintenance = last_maintenance.odo + service_interval
            last_odo = db.get_last_odo_on_car(user_id, car)
            return next_maintenance - last_odo
        return None
    except exceptions.NotFoundMaintenance:
        return None


def get_month_analytic(user_id: str, car: str) -> str:
    """Вычисление аналитики за последние 30 дней"""
    if refuelings := db.get_refuelings_list_for_month(user_id, car):
        filing_volume_sum, odo_string = get_stat_for_period(refuelings)
        return f'📊  За последние 30 дней\n\n' \
               f'🚗  {car}\n\n' \
               f'{odo_string}' \
               f'⛽  заправлено <b>{filing_volume_sum}</b> л'
    else:
        return "Заправок пока что не было"


def get_current_year_analytic(user_id: str, car: str) -> str:
    """Вычисление аналитики с начала года"""
    if refuelings := db.get_refuelings_list_for_current_year(user_id, car):
        filing_volume_sum, odo_string = get_stat_for_period(refuelings)
        return f'📊  С начала года\n\n' \
               f'🚗  {car}\n\n' \
               f'{odo_string}' \
               f'⛽  заправлено <b>{filing_volume_sum}</b> л'
    else:
        return "Заправок пока что не было"


def get_stat_for_period(data: list[Refueling]) -> tuple[int, str]:
    """Подсчет аналитики по входным данным"""
    filing_volume_sum = 0
    odo_values = []
    odo_string = ""
    for refueling in data:
        filing_volume_sum += refueling.filing_volume
        odo_values.append(refueling.odo)
    if len(odo_values) > 2:
        odo_value = max(odo_values) - min(odo_values)
        odo_string = f'📟  пройдено {odo_value} км\n\n'
    return round(filing_volume_sum, 2), odo_string
