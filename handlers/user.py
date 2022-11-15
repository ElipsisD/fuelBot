"""Работа с сообщениями от пользователя"""
import logging
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from filters.choice import OnlyKeys
from keyboards.cars_key import cars_key
from misc.states import FSMNewRefueling
from utils import db, strtime, exceptions, refuelings


async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\n\n"
                         f"Этот бот создан для ведения статистики расхода топлива твоего автомобиля\n"
                         f"Для корректных расчетов необходимо заправляться до полного бака\n"
                         f"Если ты готов внести данные о последней заправке нажми /new\n")
    # TODO Добавить инлайн-кнопку /new


async def user_start(message: types.Message, state: FSMContext):
    logging.info(f'{message.from_user.id=} {message.from_user.username=} {strtime.get_now_formatted()}')
    if db.new_user_check(str(message.from_user.id)):
        await FSMNewRefueling.adding_car.set()
        await message.answer('Введите название вашего автомобиля, '
                             'если автомобилей несколько, напишите их через ","')
    else:
        cars_list = db.user_cars(str(message.from_user.id))
        if len(cars_list) > 1:
            await FSMNewRefueling.choice_of_car.set()
            await message.answer("Какой автомобиль заправляем?", reply_markup=cars_key(cars_list))
        else:
            await FSMNewRefueling.data.set()
            async with state.proxy() as context_data:
                context_data['selected car'] = cars_list[0]
            await message.answer(f"Внеси данные в формате: объем_заправки_в_литрах общий_пробег\n"
                                 f"Пример:\n48,21 125485")


async def adding_car(message: types.Message, state: FSMContext, text):
    cars_list = re.split(r'\s*[ ,.;]\s*', message.text)
    async with state.proxy() as context_data:
        context_data['cars'] = cars_list
        if len(cars_list) > 1:
            await FSMNewRefueling.choice_of_car.set()
            await message.answer("Какой автомобиль заправляем?", reply_markup=cars_key(cars_list))
        else:
            context_data['selected car'] = cars_list[0]
            await FSMNewRefueling.data.set()
            await message.answer('Введите данные о заправке')


async def choice_of_car(message: types.Message, state: FSMContext):
    async with state.proxy() as context_data:
        context_data['selected car'] = message.text
    await FSMNewRefueling.data.set()
    await message.answer('С машиной все понятно!\n'
                         'Теперь введите данные о заправке.')


async def data(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as context_data:
            if db.new_user_check(str(message.from_user.id)):
                refuelings.add_refueling(message, context_data['cars'], context_data['selected car'])
                await message.answer('Так как это первая заправка расход будет известен в следующий раз!')
            else:
                refuelings.add_refueling(message, selected_car=context_data['selected car'])
            await state.finish()
            await message.answer('Все записал, счастливого пути!')
    except exceptions.NotCorrectRefueling as e:
        await message.answer(str(e))


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=['new'], state='*')
    dp.register_message_handler(send_welcome, commands=['start', 'help'], state='*')
    dp.register_message_handler(adding_car, state=FSMNewRefueling.adding_car)
    dp.register_message_handler(choice_of_car, OnlyKeys(), state=FSMNewRefueling.choice_of_car)
    dp.register_message_handler(data, state=FSMNewRefueling.data)
