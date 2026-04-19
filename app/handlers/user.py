import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.menu_bot import menu
from app.handlers.common import edit_callback_message

logger = logging.getLogger('telegram_logger')
router = Router(name="user")


@router.message(Command("start", "help"))
async def send_welcome(m: Message):
    """Отправляем пользователю кнопки меню и приветственный текст"""
    logger.info(f'{m.from_user.first_name} ({m.from_user.id}) ввел команду start')
    await m.answer(f"Привет, {m.from_user.first_name}!\n\n"
                   f"Этот бот создан для ведения статистики расхода топлива твоего автомобиля\n"
                   f"Для корректных расчетов необходимо заправляться до полного бака\n",
                   reply_markup=menu)
    await m.delete()


"""Меню бота"""


@router.callback_query(F.data == 'menu')
async def menu_cmd(call: CallbackQuery, state: FSMContext):
    """Отправляем пользователю кнопки меню и после нажатия кнопки НАЗАД"""
    await state.clear()
    await edit_callback_message(
        call,
        f"⬇<b>{call.from_user.first_name}</b>, выбирай⬇",
        menu,
    )


"""Общие настройки"""


@router.message()
async def delete_unnecessary_message(m: Message):
    """Удаление ненужных сообщение"""
    await m.delete()
