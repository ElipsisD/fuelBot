from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MaintenanceCallback(CallbackData, prefix="maintenance"):
    mode: str = ""
    car: str = ""


maintenance_menu_cb = MaintenanceCallback


def make_callback_maintenance_menu(mode="", car=""):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return MaintenanceCallback(mode=mode, car=car).pack()


def maintenance_menu(car: str):
    """Клавиатура вариантов работы с информацией о ТехОбслуживании"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='◀НОВОЕ ТО▶',
            callback_data=make_callback_maintenance_menu(mode='new', car=car)
        )],
        [InlineKeyboardButton(
            text='↩назад',
            callback_data='menu'
        )]
    ])


def maintenance_key(cars: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора автомобиля"""
    builder = InlineKeyboardBuilder()
    for car in cars:
        builder.row(InlineKeyboardButton(text=car, callback_data=make_callback_maintenance_menu(car=car, mode='car choice')))
    builder.row(InlineKeyboardButton(text='↩назад', callback_data='menu'))
    return builder.as_markup()
