"""Работа с сообщениями от новых пользователей пользователя"""

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from filters.filters_for_user import NewUser
from keyboards.menu_bot import for_new_user_menu, menu
from misc.states import FSMNewRefueling
from utils import db


async def welcome(m: types.Message):
    await m.answer(f"Привет, {m.from_user.first_name}!\n\n"
                   f"Когда будешь готов жми на кнопку!\n",
                   reply_markup=for_new_user_menu)
    await m.delete()


async def cars_input(call: types.CallbackQuery, state: FSMContext):
    await FSMNewRefueling.adding_car.set()
    await call.message.edit_text('Введите название вашего автомобиля!\n')
    async with state.proxy() as context_data:
        context_data['message'] = call.message


async def adding_car(m: types.Message, state: FSMContext):
    db.set_new_data(m)
    async with state.proxy() as context_data:
        prev_m = context_data['message']
    await m.delete()
    await prev_m.edit_text('Вы успешно зарегистрировались\n'
                           'Если у вас несколько автомобилей можете добавить их в разделе МОИ АВТОМОБИЛИ\n'
                           'Удачного пользования, если у вас появятся вопросы обязательно свяжитесь с разработчиком!')
    await prev_m.edit_reply_markup(reply_markup=menu)
    await state.finish()


def register_new_user(dp: Dispatcher):
    dp.register_callback_query_handler(cars_input, NewUser())
    dp.register_message_handler(adding_car, NewUser(), state=FSMNewRefueling.adding_car)
    dp.register_message_handler(welcome, NewUser(), commands=['start', 'help'], state='*')

