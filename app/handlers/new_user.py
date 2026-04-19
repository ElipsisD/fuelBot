import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.filters.filters_for_user import NewUser
from app.handlers.common import edit_message, prompt_for_state, state_data
from app.keyboards.menu_bot import for_new_user_menu, menu
from app.misc.states import FSMNewRefueling
from app.db import set_new_data

logger = logging.getLogger('telegram_logger')
router = Router(name="new_user")


@router.message(NewUser(), Command("start", "help"))
async def welcome(m: Message):
    await m.answer(f"Привет, {m.from_user.first_name}!\n\n"
                   f"Когда будешь готов жми на кнопку!\n",
                   reply_markup=for_new_user_menu)
    await m.delete()


@router.callback_query(NewUser(), F.data == "reg")
async def cars_input(call: CallbackQuery, state: FSMContext):
    await prompt_for_state(
        call,
        state,
        FSMNewRefueling.adding_car,
        'Введите название вашего автомобиля!\n',
        None,
        message=call.message,
    )


@router.message(NewUser(), FSMNewRefueling.adding_car)
async def adding_car(m: Message, state: FSMContext):
    set_new_data(m)
    context_data = await state_data(state)
    prev_m = context_data['message']
    success_text = (
        'Вы успешно зарегистрировались\n'
        'Если у вас несколько автомобилей можете добавить их в разделе МОИ АВТОМОБИЛИ\n'
        'Удачного пользования, если у вас появятся вопросы обязательно свяжитесь с разработчиком!'
    )
    await m.delete()
    await edit_message(prev_m, success_text, menu)
    logger.info(f'{m.from_user.first_name} ({m.from_user.id}) зарегистрировался')
    await state.clear()
