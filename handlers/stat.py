"""Работа с меню СТАТИСТИКА"""
from aiogram import types, Dispatcher

from keyboards.menu_bot import menu
from keyboards.stat_key import stat_cars_key, stat_menu, stat_menu_cb
from utils import db, refuelings


async def stat_choice(call: types.CallbackQuery):
    cars_list = db.user_cars(str(call.from_user.id))

    if len(cars_list) > 1:
        await call.message.edit_text("На каком авто смотрим расход?")
        await call.message.edit_reply_markup(reply_markup=stat_cars_key(cars_list))

    else:
        await call.message.edit_text("Что интересно?")
        await call.message.edit_reply_markup(reply_markup=stat_menu(cars_list[0]))


async def stat_mode_choice(call: types.CallbackQuery, callback_data: dict):
    car = callback_data.get('car')
    await call.message.edit_text("Что интересно?")
    await call.message.edit_reply_markup(reply_markup=stat_menu(car))


async def get_last_car_stat(call: types.CallbackQuery, callback_data: dict):
    answer = refuelings.last_fuel_expense(str(call.from_user.id), callback_data.get('car'))
    await call.message.edit_text(answer)
    await call.message.edit_reply_markup(reply_markup=menu)


def register_user_stat(dp: Dispatcher):
    """Регистрация хендлеров"""
    dp.register_callback_query_handler(stat_choice, text='stat')
    dp.register_callback_query_handler(stat_mode_choice, stat_menu_cb.filter(mode='car choice'))
    dp.register_callback_query_handler(get_last_car_stat, stat_menu_cb.filter(mode='mode choice'))
