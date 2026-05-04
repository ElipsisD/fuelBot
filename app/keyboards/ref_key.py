from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.menu_bot import make_callback_menu


def cars_key(cars: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора автомобиля"""
    builder = InlineKeyboardBuilder()
    for car in cars:
        builder.row(InlineKeyboardButton(text=car, callback_data=make_callback_menu(level='2', car=car)))
    builder.row(InlineKeyboardButton(text='↩назад', callback_data='menu'))
    return builder.as_markup()


def refueling_mode(car: str) -> InlineKeyboardMarkup:
    """Меню выбора типа заправки (полный бак или частичная заправка)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='‼ПОЛНЫЙ БАК‼',
            callback_data=make_callback_menu(level='3', car=car, mode='full')
        )],
        [InlineKeyboardButton(
            text='❗ЧАСТИЧНАЯ ЗАПРАВКА❗',
            callback_data=make_callback_menu(level='3', car=car, mode='partial')
        )],
        [InlineKeyboardButton(
            text='↩назад',
            callback_data='menu'
        )]
    ])
