"""Работа с сообщениями от пользователя"""
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

# from bot import bot
from keyboards.menu_bot import menu, refueling_mode, menu_cd, cars_key, back_key
from misc.states import FSMNewRefueling
from utils import db, strtime, exceptions, refuelings


async def send_welcome(message: types.Message):
    """Отправляем пользователю кнопки меню и приветственный текст"""
    await message.answer(f"Привет, {message.from_user.first_name}!\n\n"
                         f"Этот бот создан для ведения статистики расхода топлива твоего автомобиля\n"
                         f"Для корректных расчетов необходимо заправляться до полного бака\n",
                         reply_markup=menu)
    await message.delete()


async def menu_cmd(call: types.CallbackQuery):
    """Отправляем пользователю кнопки меню и после нажатия кнопки НАЗАД"""
    await call.message.edit_text(f"{call.from_user.first_name}, выбирай!")
    await call.message.edit_reply_markup(reply_markup=menu)


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
    await call.message.edit_text("Как заправляем?")
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
        answer = m.text
        await prev_m.edit_text('Успешно\n'
                               'Вы записали:\n'
                               + answer)
        await m.delete()
        await state.finish()
    except exceptions.NotCorrectRefueling as e:
        await m.delete()
        await prev_m.edit_text(str(e))
        await prev_m.edit_reply_markup(reply_markup=back_key)


def register_user(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_callback_query_handler(menu_cmd, menu_cd.filter(level='0'), state='*')
    dp.register_callback_query_handler(new_cmd, text_contains='new ref')
    dp.register_callback_query_handler(choice_of_refueling_mode, menu_cd.filter(level='2'))
    dp.register_callback_query_handler(data_input, menu_cd.filter(level='3'))
    dp.register_message_handler(data_handler, state=FSMNewRefueling.data)
