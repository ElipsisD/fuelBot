from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class SettingsCallback(CallbackData, prefix="settings"):
    mode: str = ""


settings_menu_cb = SettingsCallback


def make_callback_settings_menu(mode=""):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return SettingsCallback(mode=mode).pack()


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
