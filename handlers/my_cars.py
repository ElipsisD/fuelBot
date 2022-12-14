"""Работа с разделом МОИ АВТОМОБИЛИ"""
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.cars_key import actions_with_cars, actions_cars_key, actions_menu
from keyboards.menu_bot import back_key, menu
from misc.states import FSMActions
from utils import db
from utils.exceptions import NotCorrectCarName

logger = logging.getLogger('telegram_logger')


async def menu_cars_cmd(call: types.CallbackQuery):
    cars = db.user_cars(str(call.from_user.id))
    await call.message.edit_text('\n'.join(cars))
    await call.message.edit_reply_markup(reply_markup=actions_with_cars(cars))


async def adding_car(call: types.CallbackQuery, state: FSMContext):
    await FSMActions.new_car_name.set()
    async with state.proxy() as context_data:
        context_data['prev_m'] = call.message
    await call.message.edit_text('Введите название нового автомобиля')
    await call.message.edit_reply_markup(reply_markup=back_key)


async def new_car_handler(m: types.Message, state: FSMContext):
    async with state.proxy() as context_data:
        prev_m = context_data['prev_m']
    try:
        car_name = m.text
        if len(car_name) > 60:
            raise NotCorrectCarName('Слишком длинное название!\nПопробуй еще раз')
        db.add_new_car(str(m.from_user.id), car_name)
        await prev_m.edit_text('Добавлен новый автомобиль!\n\n' + car_name)
        logger.info(f'{m.from_user.first_name} добавил новый авто: {car_name}')
        await prev_m.edit_reply_markup(reply_markup=menu)
        await m.delete()
        await state.finish()
    except NotCorrectCarName as e:
        await m.delete()
        await prev_m.edit_text(str(e))
        await prev_m.edit_reply_markup(reply_markup=back_key)


async def deleting_car(call: types.CallbackQuery):
    cars_list = db.user_cars(str(call.from_user.id))
    await call.message.edit_text('Какой автомобиль удалить из бота?')
    await call.message.edit_reply_markup(reply_markup=actions_cars_key(cars_list))


async def choice_car_to_delete(call: types.CallbackQuery, callback_data: dict):
    car = callback_data.get('car')
    db.delete_car(str(call.from_user.id), car)
    await call.message.edit_text(f'Автомобиль {callback_data.get("car")} удален!')
    logger.info(f'{call.from_user.first_name} удалил автомобиль: {car}')
    await call.message.edit_reply_markup(reply_markup=menu)


def register_user_my_cars(dp: Dispatcher):
    """Регистрация хендлеров"""
    dp.register_callback_query_handler(menu_cars_cmd, text='action menu cars')
    dp.register_callback_query_handler(adding_car, actions_menu.filter(mode='add car'))
    dp.register_message_handler(new_car_handler, state=FSMActions.new_car_name)
    dp.register_callback_query_handler(deleting_car, actions_menu.filter(mode='delete car'))
    dp.register_callback_query_handler(choice_car_to_delete, actions_menu.filter(mode='choice'))
