"""Работа с сообщениями от пользователя"""
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.menu_bot import menu

logger = logging.getLogger('telegram_logger')

async def send_welcome(m: types.Message):
    """Отправляем пользователю кнопки меню и приветственный текст"""
    logger.info(f'{m.from_user.first_name} ({m.from_user.id}) ввел команду start')
    await m.answer(f"Привет, {m.from_user.first_name}!\n\n"
                   f"Этот бот создан для ведения статистики расхода топлива твоего автомобиля\n"
                   f"Для корректных расчетов необходимо заправляться до полного бака\n",
                   reply_markup=menu)
    await m.delete()


"""Меню бота"""


async def menu_cmd(call: types.CallbackQuery, state: FSMContext):
    """Отправляем пользователю кнопки меню и после нажатия кнопки НАЗАД"""
    await state.finish()
    await call.message.edit_text(f"⬇<b>{call.from_user.first_name}</b>, выбирай⬇")
    await call.message.edit_reply_markup(reply_markup=menu)


"""Общие настройки"""


async def delete_unnecessary_message(m: types.Message):
    """Удаление ненужных сообщение"""
    await m.delete()


def register_user(dp: Dispatcher):
    """Регистрация хендлеров"""
    """Старт"""
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    """Меню"""
    dp.register_callback_query_handler(menu_cmd, text='menu', state='*')
    """Общий"""
    dp.register_message_handler(delete_unnecessary_message, state='*')
