"""Работа с сообщениями от новых пользователей пользователя"""
import logging
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from filters.filters_for_user import OnlyKeys, NewUser
from keyboards.Inlinenew import new_key
from misc.states import FSMNewRefueling
from utils import db, strtime, exceptions, refuelings


async def welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\n\n"
                         f"это сообщение для новеньких",
                         reply_markup=new_key)
    # TODO Добавить инлайн-кнопку /new
    #  Необходимо ввести фильтр для определения новых пользователей и создать отдельные хендлеры (в отдельном файле) для их обработки
    # TODO Добавить эмодзи
    # TODO на этапе получения списка авто надо добавить пользователя в базу отдельной функцией, чтобы отделить работу с новым пользователя

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


def register_new_user(dp: Dispatcher):
    dp.register_message_handler(welcome, NewUser(), commands=['start', 'help'], state='*')
