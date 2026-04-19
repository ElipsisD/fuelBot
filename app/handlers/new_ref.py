import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.handlers.common import (
    answer_with_main_menu,
    edit_callback_message,
    edit_message,
    prompt_for_state,
    state_data,
)
from app.keyboards.menu_bot import RefuelingCallback, back_key
from app.keyboards.ref_key import cars_key, refueling_mode
from app.misc.states import FSMNewRefueling
from app.db import user_cars
from app.utils import strtime, refuelings, exceptions
from app.utils.refuelings import update_graph_stat

logger = logging.getLogger('telegram_logger')
router = Router(name="new_ref")


@router.callback_query(F.data == 'new ref')
async def new_cmd(call: CallbackQuery):
    logging.info(f'{call.from_user.id=} {call.from_user.username=} {strtime.get_now_formatted()}')
    cars_list = user_cars(str(call.from_user.id))
    if len(cars_list) > 1:
        await edit_callback_message(call, "Какой автомобиль заправляем?", cars_key(cars_list))
    else:
        await edit_callback_message(call, "Как заправляем?", refueling_mode(cars_list[0]))


@router.callback_query(RefuelingCallback.filter(F.level == '2'))
async def choice_of_refueling_mode(call: CallbackQuery, callback_data: RefuelingCallback):
    car = callback_data.car
    await edit_callback_message(call, f"Автомобиль: <b>{car}</b>\n\nКак заправляем?", refueling_mode(car))


@router.callback_query(RefuelingCallback.filter(F.level == '3'))
async def data_input(call: CallbackQuery, callback_data: RefuelingCallback, state: FSMContext):
    answer = "Внеси данные в формате:\n" + \
             ("объем_заправки_в_литрах общий_пробег\nПример:\n48,21 125485"
              if callback_data.mode == 'full'
              else "объем_заправки_в_литрах\nПример:\n48,21")
    await prompt_for_state(
        call,
        state,
        FSMNewRefueling.data,
        answer,
        back_key,
        car=callback_data.car,
        mode=callback_data.mode,
        message=call.message,
    )


@router.message(FSMNewRefueling.data)
async def data_handler(m: Message, state: FSMContext):
    context_data = await state_data(state)
    car = context_data['car']
    prev_m = context_data['message']
    ref_mode = context_data['mode']
    try:
        refuelings.add_refueling(m, ref_mode=ref_mode, selected_car=car)
        if ref_mode == 'full':
            answer = refuelings.last_fuel_expense(str(m.from_user.id), car=car)
        else:
            answer = refuelings.volume_since_last_full_fill(str(m.from_user.id), car=car)
        logger.info(f'{m.from_user.first_name} заправил:\n{answer}')
        await edit_message(prev_m, answer)
        await answer_with_main_menu(m, m.from_user.first_name)
        try:
            update_graph_stat(str(m.from_user.id), car)
        except exceptions.NotEnoughRefuelings:
            pass
        await m.delete()
        await state.clear()
    except (exceptions.NotCorrectRefueling, exceptions.NotEnoughRefuelings) as e:
        await m.delete()
        await edit_message(prev_m, str(e), back_key)
