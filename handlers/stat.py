"""Работа с меню СТАТИСТИКА"""
import logging

from aiogram import types, Dispatcher

from keyboards.menu_bot import menu, back_key
from keyboards.stat_key import stat_cars_key, stat_menu, stat_menu_cb
from utils import db, refuelings, exceptions
from utils.refuelings import graph_stat

logger = logging.getLogger('telegram_logger')


async def stat_choice(call: types.CallbackQuery):
    """Выбор автомобиля."""
    cars_list = db.user_cars(str(call.from_user.id))

    if len(cars_list) > 1:
        await call.message.edit_text("На каком авто смотрим расход?")
        await call.message.edit_reply_markup(reply_markup=stat_cars_key(cars_list))

    else:
        await call.message.edit_text("Что интересно?")
        await call.message.edit_reply_markup(reply_markup=stat_menu(cars_list[0]))


async def stat_mode_choice(call: types.CallbackQuery, callback_data: dict):
    """Выбор вида аналитики."""
    car = callback_data.get('car')
    await call.message.edit_text("Что интересно?")
    await call.message.edit_reply_markup(reply_markup=stat_menu(car))


async def get_last_car_stat(call: types.CallbackQuery, callback_data: dict):
    """Отправка последнего расхода на автомобиле."""
    try:
        car = callback_data.get('car')
        answer = refuelings.last_fuel_expense(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел свой последний расход на {car}')
        await call.message.edit_text(answer)
        await call.message.edit_reply_markup(reply_markup=menu)
    except exceptions.NotEnoughRefuelings as e:
        await call.message.edit_text(str(e))
        await call.message.edit_reply_markup(reply_markup=menu)


async def get_graph_stat(call: types.CallbackQuery, callback_data: dict):
    """Отправка графика расхода топлива на автомобиле за все заправки."""
    car = callback_data.get('car')
    try:
        photo_url = graph_stat(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел график расхода на {car}')
        await call.message.edit_text('⬇График за весь период заправок⬇')
        await call.message.answer_photo(photo_url)
        await call.message.answer(f"⬇<b>{call.from_user.first_name}</b>, выбирай⬇", reply_markup=menu)

    except exceptions.NotEnoughRefuelings as e:
        await call.message.edit_text(str(e))
        await call.message.edit_reply_markup(reply_markup=back_key)


async def get_month_stat(call: types.CallbackQuery, callback_data: dict):
    """Отправка аналитики за последние 30 дней на автомобиле."""
    car = callback_data.get('car')
    try:
        answer = refuelings.get_month_analytic(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел аналитику за последние 30 дней на {car}')
        await call.message.edit_text(answer)
        await call.message.answer(f"⬇<b>{call.from_user.first_name}</b>, выбирай⬇", reply_markup=menu)

    except exceptions.NotEnoughRefuelings as e:
        await call.message.edit_text(str(e))
        await call.message.edit_reply_markup(reply_markup=back_key)


async def get_current_year_stat(call: types.CallbackQuery, callback_data: dict):
    """Отправка аналитики с начала года на автомобиле."""
    car = callback_data.get('car')
    try:
        answer = refuelings.get_current_year_analytic(str(call.from_user.id), car)
        logger.info(f'{call.from_user.first_name} посмотрел аналитику с начала года на {car}')
        await call.message.edit_text(answer)
        await call.message.answer(f"⬇<b>{call.from_user.first_name}</b>, выбирай⬇", reply_markup=menu)

    except exceptions.NotEnoughRefuelings as e:
        await call.message.edit_text(str(e))
        await call.message.edit_reply_markup(reply_markup=back_key)


def register_user_stat(dp: Dispatcher):
    """Регистрация хендлеров."""
    dp.register_callback_query_handler(stat_choice, text='stat')
    dp.register_callback_query_handler(stat_mode_choice, stat_menu_cb.filter(mode='car choice'))
    dp.register_callback_query_handler(get_last_car_stat, stat_menu_cb.filter(mode='mode choice'))
    dp.register_callback_query_handler(get_graph_stat, stat_menu_cb.filter(mode='graph'))
    dp.register_callback_query_handler(get_current_year_stat, stat_menu_cb.filter(mode='year'))
    dp.register_callback_query_handler(get_month_stat, stat_menu_cb.filter(mode='month'))
