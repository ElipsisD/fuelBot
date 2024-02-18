from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

settings_menu_cb = CallbackData('Settings', 'mode')


def make_callback_settings_menu(mode=''):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return settings_menu_cb.new(mode=mode)


def settings_menu():
    """Клавиатура вариантов работы с информацией о Настройках"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='◀ИЗМЕНИТЬ ПОСЛЕДНИЕ ДАННЫЕ О ЗАПРАВКЕ▶',
            callback_data=make_callback_settings_menu(mode='change_last_ref')
        )],
        [InlineKeyboardButton(
            text='◀ИЗМЕНИТЬ ИНТЕРВАЛ▶',
            callback_data=make_callback_settings_menu(mode='interval')
        )],
        [InlineKeyboardButton(
            text='↩назад',
            callback_data='menu'
        )]
    ])
