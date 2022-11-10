import logging

from utils import db, strtime, exceptions
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from utils import refuelings


class FSMUser(StatesGroup):
    adding_car = State()
    choice_of_car = State()
    data = State()


async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\n\n"
                         f"Для корректных расчетов необходимо заправлять до полного бака\n"
                         f"Чтобы внести данные о последней заправке нажми /new\n")


async def user_start(message: types.Message, state: FSMContext):
    logging.info(f'{message.from_user.id=} {message.from_user.username=} {strtime.get_now_formatted()}')
    if db.new_user_check(str(message.from_user.id)):
        await FSMUser.adding_car.set()
        await message.answer('Введите название вашего автомобиля, '
                             'если автомобилей несколько, напишите их через ","')
    else:
        car_list = db.user_cars(str(message.from_user.id))
        if len(car_list) > 1:
            await FSMUser.choice_of_car.set()
            cars_list = [f'{i}) {car}' for i, car in enumerate(car_list, 1)]
            await message.answer('Какой автомобиль заправляем?\n'
                                 'Напишите цифру, соответствующую автомобилю\n\n' +
                                 ("\n".join(cars_list)))
        else:
            await FSMUser.data.set()
            async with state.proxy() as context_data:
                context_data['selected car'] = car_list[0]
            await message.answer(f"Внеси данные в формате: объем_заправки_в_литрах общий_пробег\n"
                                 f"Пример:\n48,21 125485")


async def adding_car(message: types.Message, state: FSMContext):
    cars_list = message.text.split(',')
    async with state.proxy() as context_data:
        context_data['cars'] = cars_list
        if len(cars_list) > 1:
            await FSMUser.choice_of_car.set()
            cars_list = [f'{i}) {car}' for i, car in enumerate(cars_list, 1)]
            await message.answer('Какой автомобиль заправляем?\n'
                                 'Напишите цифру, соответствующую автомобилю\n\n' +
                                 ("\n".join(cars_list)))
        else:
            context_data['selected car'] = cars_list[0]
            await FSMUser.data.set()
            await message.answer('Введите данные о заправке')


async def choice_of_car(message: types.Message, state: FSMContext):
    async with state.proxy() as context_data:
        if db.new_user_check(str(message.from_user.id)):
            context_data['selected car'] = context_data['cars'][int(message.text) - 1]
        else:
            context_data['selected car'] = db.user_cars(str(message.from_user.id))[int(message.text) - 1]
    await FSMUser.data.set()
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
    dp.register_message_handler(adding_car, state=FSMUser.adding_car)
    dp.register_message_handler(choice_of_car, state=FSMUser.choice_of_car)
    dp.register_message_handler(data, state=FSMUser.data)


# @dp.message_handler()
# async def add_refueling(message: types.Message):
#     """Добавление данных о новой заправке"""
#     try:
#         refueling = refuelings.add_refueling(message)
#     except exceptions.NotCorrectRefueling as e:
#         await message.answer(str(e))
#         return
#     answer_message = (
#         'Данные о заправке добавлены!\n'
#     )
#     await message.answer(answer_message)
