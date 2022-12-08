"""Работа с разделом ЛОГАМИ"""
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from keyboards.cars_key import actions_with_cars, actions_cars_key, actions_menu
from keyboards.menu_bot import back_key, menu
from misc.states import FSMActions
from utils import db
from utils.exceptions import NotCorrectCarName


async def echo_message(m: types.Message):
    """ЭХО"""
    # await m.answer(m.chat.id)
    await m.bot.send_message(m.chat.id, m.text)


def register_logs(dp: Dispatcher):
    """Регистрация хендлеров"""
    dp.register_message_handler(echo_message, ChatTypeFilter(chat_type=types.ChatType.GROUP))