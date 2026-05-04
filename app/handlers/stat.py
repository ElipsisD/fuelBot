import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.handlers.common import answer_with_main_menu, edit_callback_message, edit_message
from app.keyboards.menu_bot import menu, back_key
from app.keyboards.stat_key import StatCallback, stat_cars_key, stat_menu
from app.db import user_cars
from app.utils import refuelings, exceptions
from app.utils.refuelings import graph_stat

logger = logging.getLogger('telegram_logger')
router = Router(name="stat")


@router.callback_query(F.data == 'stat')
async def stat_choice(call: CallbackQuery):
    """Выбор автомобиля."""
    cars_list = user_cars(str(call.from_user.id))
    if len(cars_list) > 1:
        await edit_callback_message(call, "На каком авто смотрим расход?", stat_cars_key(cars_list))
    else:
        await edit_callback_message(call, "Что интересно?", stat_menu(cars_list[0]))


@router.callback_query(StatCallback.filter(F.mode == 'car choice'))
async def stat_mode_choice(call: CallbackQuery, callback_data: StatCallback):
    """Выбор вида аналитики."""
    car = callback_data.car
    await edit_callback_message(call, "Что интересно?", stat_menu(car))


@router.callback_query(StatCallback.filter(F.mode == 'mode choice'))
async def get_last_car_stat(call: CallbackQuery, callback_data: StatCallback):
    """Отправка последнего расхода на автомобиле."""
    car = callback_data.car
    try:
        answer = refuelings.last_fuel_expense(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел свой последний расход на {car}')
        await edit_callback_message(call, answer, menu)
    except exceptions.NotEnoughRefuelings as e:
        await edit_callback_message(call, str(e), menu)
    except ZeroDivisionError as e:
        await edit_callback_message(call, str(e), menu)


@router.callback_query(StatCallback.filter(F.mode == 'graph'))
async def get_graph_stat(call: CallbackQuery, callback_data: StatCallback):
    """Отправка графика расхода топлива на автомобиле за все заправки."""
    car = callback_data.car
    try:
        photo_url = graph_stat(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел график расхода на {car}')
        await edit_message(call.message, '⬇График за весь период заправок⬇')
        await call.message.answer_photo(photo_url)
        await answer_with_main_menu(call.message, call.from_user.first_name)
        await call.answer()
    except exceptions.NotEnoughRefuelings as e:
        await edit_callback_message(call, str(e), back_key)


@router.callback_query(StatCallback.filter(F.mode == 'month'))
async def get_month_stat(call: CallbackQuery, callback_data: StatCallback):
    """Отправка аналитики за последние 30 дней на автомобиле."""
    car = callback_data.car
    try:
        answer = refuelings.get_month_analytic(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел аналитику за последние 30 дней на {car}')
        await edit_message(call.message, answer)
        await answer_with_main_menu(call.message, call.from_user.first_name)
        await call.answer()
    except exceptions.NotEnoughRefuelings as e:
        await edit_callback_message(call, str(e), back_key)


@router.callback_query(StatCallback.filter(F.mode == 'year'))
async def get_current_year_stat(call: CallbackQuery, callback_data: StatCallback):
    """Отправка аналитики с начала года на автомобиле."""
    car = callback_data.car
    try:
        answer = refuelings.get_current_year_analytic(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел аналитику с начала года на {car}')
        await edit_message(call.message, answer)
        await answer_with_main_menu(call.message, call.from_user.first_name)
        await call.answer()
    except exceptions.NotEnoughRefuelings as e:
        await edit_callback_message(call, str(e), back_key)
