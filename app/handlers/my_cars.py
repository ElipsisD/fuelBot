import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.handlers.common import edit_callback_message, edit_message, prompt_for_state, state_data
from app.keyboards.cars_key import CarsCallback, actions_with_cars, actions_cars_key
from app.keyboards.menu_bot import back_key, menu
from app.misc.states import FSMActions
from app.db import add_new_car, delete_car, user_cars
from app.utils.exceptions import NotCorrectCarName

logger = logging.getLogger('telegram_logger')
router = Router(name="my_cars")


@router.callback_query(F.data == 'action menu cars')
async def menu_cars_cmd(call: CallbackQuery):
    cars = user_cars(str(call.from_user.id))
    await edit_callback_message(call, '\n'.join(cars), actions_with_cars(cars))


@router.callback_query(CarsCallback.filter(F.mode == 'add car'))
async def adding_car(call: CallbackQuery, state: FSMContext):
    await prompt_for_state(
        call,
        state,
        FSMActions.new_car_name,
        'Введите название нового автомобиля',
        back_key,
        prev_m=call.message,
    )


@router.message(FSMActions.new_car_name)
async def new_car_handler(m: Message, state: FSMContext):
    context_data = await state_data(state)
    prev_m = context_data['prev_m']
    try:
        car_name = m.text
        if len(car_name) > 60:
            raise NotCorrectCarName('Слишком длинное название!\nПопробуй еще раз')
        add_new_car(str(m.from_user.id), car_name)
        await edit_message(prev_m, 'Добавлен новый автомобиль!\n\n' + car_name, menu)
        logger.info(f'{m.from_user.first_name} добавил новый авто: {car_name}')
        await m.delete()
        await state.clear()
    except NotCorrectCarName as e:
        await m.delete()
        await edit_message(prev_m, str(e), back_key)


@router.callback_query(CarsCallback.filter(F.mode == 'delete car'))
async def deleting_car(call: CallbackQuery):
    cars_list = user_cars(str(call.from_user.id))
    await edit_callback_message(call, 'Какой автомобиль удалить из бота?', actions_cars_key(cars_list))


@router.callback_query(CarsCallback.filter(F.mode == 'choice'))
async def choice_car_to_delete(call: CallbackQuery, callback_data: CarsCallback):
    car = callback_data.car
    delete_car(str(call.from_user.id), car)
    await edit_callback_message(call, f'Автомобиль {car} удален!', menu)
    logger.info(f'{call.from_user.first_name} удалил автомобиль: {car}')
