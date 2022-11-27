"""Работа с добавлением информации о новой заправке"""
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.menu_bot import back_key, menu, menu_cd
from keyboards.ref_key import cars_key, refueling_mode
from misc.states import FSMNewRefueling
from utils import db, strtime, refuelings, exceptions


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
        answer = answer if ref_mode == 'full' else 'Успешно 👌'
        await prev_m.edit_text(answer)
        await prev_m.edit_reply_markup(reply_markup=menu)
        await m.delete()
        await state.finish()
    except exceptions.NotCorrectRefueling as e:
        await m.delete()
        await prev_m.edit_text(str(e))
        await prev_m.edit_reply_markup(reply_markup=back_key)


def register_user_new_ref(dp: Dispatcher):
    """Регистрация хендлеров"""
    dp.register_callback_query_handler(new_cmd, text='new ref')
    dp.register_callback_query_handler(choice_of_refueling_mode, menu_cd.filter(level='2'))
    dp.register_callback_query_handler(data_input, menu_cd.filter(level='3'))
    dp.register_message_handler(data_handler, state=FSMNewRefueling.data)
