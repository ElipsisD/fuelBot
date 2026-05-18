import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.handlers.common import edit_callback_message, edit_message, prompt_for_state, state_data
from app.keyboards.maintenance_key import MaintenanceCallback, maintenance_key, maintenance_menu
from app.keyboards.menu_bot import menu, back_key
from app.misc.states import FSMMaintenance
from app.db import Maintenance, new_maintenance, user_cars
from app.utils import exceptions, maintenance_info
from app.utils.maintenance_info import make_maintenance_info

logger = logging.getLogger('telegram_logger')
router = Router(name="maintenance")


@router.callback_query(F.data == 'maintenance')
async def choice(call: CallbackQuery):
    """Выбор автомобиля"""
    cars_list = user_cars(str(call.from_user.id))
    if len(cars_list) > 1:
        await edit_callback_message(call, "На каком авто смотрим информацию о ТО?", maintenance_key(cars_list))
    else:
        answer = make_maintenance_info(str(call.from_user.id), cars_list[0])
        await edit_callback_message(call, answer, maintenance_menu(cars_list[0]))


@router.callback_query(MaintenanceCallback.filter(F.mode == 'car choice'))
async def mode_choice(call: CallbackQuery, callback_data: MaintenanceCallback):
    """Отображение информации и меню"""
    car = callback_data.car
    answer = make_maintenance_info(str(call.from_user.id), car)
    await edit_callback_message(call, answer, maintenance_menu(car))


@router.callback_query(MaintenanceCallback.filter(F.mode == 'new'))
async def new_maintenance_handler(call: CallbackQuery, state: FSMContext, callback_data: MaintenanceCallback):
    """Реакция на кнопку НОВОЕ ТО"""
    await prompt_for_state(
        call,
        state,
        FSMMaintenance.new_maintenance_date,
        'Введите дату проведения ТО в формате:\n\n<b>ДД.ММ.ГГ</b>',
        back_key,
        prev_m=call.message,
        car=callback_data.car,
    )


@router.message(FSMMaintenance.new_maintenance_date)
async def date_handler(m: Message, state: FSMContext):
    """Валидация даты ТО"""
    context_data = await state_data(state)
    prev_m = context_data['prev_m']
    try:
        date = maintenance_info.parse_maintenance_date(m.text)
        await state.update_data(date=date)
        await edit_message(prev_m, 'Введите пробег автомобиля, на котором было проведено ТО', back_key)
        await state.set_state(FSMMaintenance.new_maintenance_odo)
        await m.delete()
    except exceptions.NotCorrectData as e:
        await m.delete()
        await edit_message(prev_m, str(e), back_key)


@router.message(FSMMaintenance.new_maintenance_odo)
async def odo_handler(m: Message, state: FSMContext):
    """Валидация пробега ТО и запись в БД"""
    context_data = await state_data(state)
    prev_m = context_data['prev_m']
    date = context_data['date']
    car = context_data['car']
    try:
        odo = maintenance_info.parse_maintenance_number(m.text)
        new_maintenance(str(m.from_user.id), Maintenance(date, car, odo))
        await edit_message(prev_m, 'Информация о ТО успешно записана!', menu)
        logger.info(f'{m.from_user.first_name} ввел данные о новом ТО')
        await m.delete()
        await state.clear()
    except exceptions.NotCorrectNumber as e:
        await m.delete()
        await edit_message(prev_m, str(e), back_key)
