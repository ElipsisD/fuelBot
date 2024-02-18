"""Работа с меню ТО"""
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.maintenance_key import maintenance_key, maintenance_menu, maintenance_menu_cb
from keyboards.menu_bot import menu, back_key
from misc.states import FSMMaintenance
from utils import db, exceptions, maintenance_info
from utils.db import Maintenance
from utils.maintenance_info import make_maintenance_info

logger = logging.getLogger('telegram_logger')


async def choice(call: types.CallbackQuery):
    """Выбор автомобиля"""
    cars_list = db.user_cars(str(call.from_user.id))

    if len(cars_list) > 1:
        await call.message.edit_text("На каком авто смотрим информацию о ТО?")
        await call.message.edit_reply_markup(reply_markup=maintenance_key(cars_list))

    else:
        answer = make_maintenance_info(str(call.from_user.id), cars_list[0])
        await call.message.edit_text(answer)
        await call.message.edit_reply_markup(reply_markup=maintenance_menu(cars_list[0]))


async def mode_choice(call: types.CallbackQuery, callback_data: dict):
    """Отображение информации и меню"""
    car = callback_data.get('car')
    answer = make_maintenance_info(str(call.from_user.id), car)
    await call.message.edit_text(answer)
    await call.message.edit_reply_markup(reply_markup=maintenance_menu(car))


async def new_maintenance(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    """Реакция на кнопку НОВОЕ ТО"""
    await FSMMaintenance.new_maintenance_date.set()
    async with state.proxy() as context_data:
        context_data['prev_m'] = call.message
        context_data['car'] = callback_data.get('car')
    await call.message.edit_text('Введите дату проведения ТО в формате:\n\n<b>ДД.ММ.ГГ</b>')
    await call.message.edit_reply_markup(reply_markup=back_key)


async def date_handler(m: types.Message, state: FSMContext):
    """Валидация даты ТО"""
    async with state.proxy() as context_data:
        prev_m = context_data['prev_m']
        try:
            date = maintenance_info.parse_maintenance_date(m.text)
            context_data['date'] = date
            await prev_m.edit_text('Введите пробег автомобиля, на котором было проведено ТО')
            await prev_m.edit_reply_markup(reply_markup=back_key)
            await FSMMaintenance.new_maintenance_odo.set()
            await m.delete()
        except exceptions.NotCorrectData as e:
            await m.delete()
            await prev_m.edit_text(str(e))
            await prev_m.edit_reply_markup(reply_markup=back_key)


async def odo_handler(m: types.Message, state: FSMContext):
    """Валидация пробега ТО и запись в БД"""
    async with state.proxy() as context_data:
        prev_m = context_data['prev_m']
        date = context_data['date']
        car = context_data['car']
    try:
        odo = maintenance_info.parse_maintenance_number(m.text)
        db.new_maintenance(str(m.from_user.id), Maintenance(date, car, odo))
        await prev_m.edit_text('Информация о ТО успешно записана!')
        await prev_m.edit_reply_markup(reply_markup=menu)
        logger.info(f'{m.from_user.first_name} ввел данные о новом ТО')
        await m.delete()
        await state.finish()
    except exceptions.NotCorrectNumber as e:
        await m.delete()
        await prev_m.edit_text(str(e))
        await prev_m.edit_reply_markup(reply_markup=back_key)


def register_user_maintenance(dp: Dispatcher):
    """Регистрация хендлеров"""
    dp.register_callback_query_handler(choice, text='maintenance')
    dp.register_callback_query_handler(mode_choice, maintenance_menu_cb.filter(mode='car choice'))
    dp.register_callback_query_handler(new_maintenance, maintenance_menu_cb.filter(mode='new'))
    dp.register_message_handler(date_handler, state=FSMMaintenance.new_maintenance_date)
    dp.register_message_handler(odo_handler, state=FSMMaintenance.new_maintenance_odo)
