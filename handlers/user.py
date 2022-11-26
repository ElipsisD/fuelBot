"""Работа с сообщениями от пользователя"""
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.cars_key import actions_with_cars, actions_menu, actions_cars_key
from keyboards.menu_bot import menu, menu_cd, back_key
from keyboards.ref_key import refueling_mode, cars_key
from misc.states import FSMNewRefueling, FSMActions
from utils import db, strtime, exceptions, refuelings
from utils.exceptions import NotCorrectCarName


async def send_welcome(m: types.Message):
    """Отправляем пользователю кнопки меню и приветственный текст"""
    await m.answer(f"Привет, {m.from_user.first_name}!\n\n"
                   f"Этот бот создан для ведения статистики расхода топлива твоего автомобиля\n"
                   f"Для корректных расчетов необходимо заправляться до полного бака\n",
                   reply_markup=menu)
    await m.delete()


"""Меню бота"""


async def menu_cmd(call: types.CallbackQuery, state: FSMContext):
    """Отправляем пользователю кнопки меню и после нажатия кнопки НАЗАД"""
    await state.finish()
    await call.message.edit_text(f"{call.from_user.first_name}, выбирай! 😅")
    await call.message.edit_reply_markup(reply_markup=menu)


"""Работа с добавлением информации о новой заправке"""


async def new_cmd(call: types.CallbackQuery):
    logging.info(f'{call.from_user.id=} {call.from_user.username=} {strtime.get_now_formatted()}')
    cars_list = db.user_cars(str(call.from_user.id))

    if len(cars_list) > 1:
        await call.message.edit_text("Какой автомобиль заправляем?")
        await call.message.edit_reply_markup(reply_markup=cars_key(cars_list))

    else:
        await call.message.edit_text("Как заправляем?")
        await call.message.edit_reply_markup(reply_markup=refueling_mode(cars_list[0]))


async def choice_of_refueling_mode(call: types.CallbackQuery, callback_data: dict):
    car = callback_data.get('car')
    await call.message.edit_text(f"Автомобиль: {car}\n\n"
                                 "Как заправляем?")
    await call.message.edit_reply_markup(reply_markup=refueling_mode(car))


async def data_input(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await FSMNewRefueling.data.set()
    async with state.proxy() as context_data:
        context_data.update(callback_data)
        context_data['message'] = call.message
    answer = "Внеси данные в формате:\n" + \
             ("объем_заправки_в_литрах общий_пробег\nПример:\n48,21 125485"
              if callback_data['mode'] == 'full'
              else "объем_заправки_в_литрах\nПример:\n48,21")

    await call.message.edit_text(answer)
    await call.message.edit_reply_markup(reply_markup=back_key)


async def data_handler(m: types.Message, state: FSMContext):
    async with state.proxy() as context_data:
        car = context_data['car']
        prev_m = context_data['message']
        ref_mode = context_data['mode']
    try:
        refuelings.add_refueling(m, ref_mode=ref_mode, selected_car=car)
        answer = refuelings.last_fuel_expense(str(m.from_user.id), car=car)
        answer = answer if ref_mode == 'full' else ''
        await prev_m.edit_text('Успешно\n'
                               f'Автомобиль: {car}\n'
                               + answer)  # TODO Если заправка промежуточная, то не надо выводить расход
        await prev_m.edit_reply_markup(reply_markup=menu)
        await m.delete()
        await state.finish()
    except exceptions.NotCorrectRefueling as e:
        await m.delete()
        await prev_m.edit_text(str(e))
        await prev_m.edit_reply_markup(reply_markup=back_key)


"""Работа с разделом МОИ АВТОМОБИЛИ"""


async def menu_cars_cmd(call: types.CallbackQuery):
    cars = db.user_cars(str(call.from_user.id))
    if len(cars) == 1:
        await call.message.edit_text(cars[0])
    else:
        await call.message.edit_text('\n'.join(cars))
    await call.message.edit_reply_markup(reply_markup=actions_with_cars)


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
        db.add_new_car(str(m.from_user.id), m.text)
        await prev_m.edit_text('Добавлен новый автомобиль!\n\n'+m.text)
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
    db.delete_car(str(call.from_user.id), callback_data.get('car'))
    await call.message.edit_text(f'Автомобиль {callback_data.get("car")} удален!')
    await call.message.edit_reply_markup(reply_markup=menu)


"""Общие настройки"""


async def delete_unnecessary_message(m: types.Message):
    """Удаление ненужных сообщение"""
    await m.delete()


def register_user(dp: Dispatcher):
    """Регистрация всех хендлеров"""
    """Старт"""
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    """Меню"""
    dp.register_callback_query_handler(menu_cmd, text='menu', state='*')
    """Новая заправка"""
    dp.register_callback_query_handler(new_cmd, text='new ref')
    dp.register_callback_query_handler(choice_of_refueling_mode, menu_cd.filter(level='2'))
    dp.register_callback_query_handler(data_input, menu_cd.filter(level='3'))
    dp.register_message_handler(data_handler, state=FSMNewRefueling.data)
    """Меню действий с автомобилями"""
    dp.register_callback_query_handler(menu_cars_cmd, text='action menu cars')
    dp.register_callback_query_handler(adding_car, actions_menu.filter(mode='add car'))
    dp.register_message_handler(new_car_handler, state=FSMActions.new_car_name)
    dp.register_callback_query_handler(deleting_car, actions_menu.filter(mode='delete car'))
    dp.register_callback_query_handler(choice_car_to_delete, actions_menu.filter(mode='choice'))
    """Общий"""
    dp.register_message_handler(delete_unnecessary_message, state='*')
