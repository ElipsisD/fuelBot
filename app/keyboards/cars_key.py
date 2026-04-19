from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CarsCallback(CallbackData, prefix="cars"):
    mode: str = ""
    car: str = ""


actions_menu = CarsCallback


def make_callback_actions_menu(mode="", car=""):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return CarsCallback(mode=mode, car=car).pack()


def actions_with_cars(cars: list):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🆕ДОБАВИТЬ АВТО🆕', callback_data=make_callback_actions_menu(mode='add car')))
    if len(cars) > 1:
        builder.row(InlineKeyboardButton(text='🚮УДАЛИТЬ АВТО🚮', callback_data=make_callback_actions_menu(mode='delete car')))
    builder.row(InlineKeyboardButton(text='↩назад', callback_data='menu'))
    return builder.as_markup()


def actions_cars_key(cars: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора автомобиля"""
    builder = InlineKeyboardBuilder()
    for car in cars:
        builder.row(InlineKeyboardButton(text=car, callback_data=make_callback_actions_menu(car=car, mode='choice')))
    builder.row(InlineKeyboardButton(text='↩назад', callback_data='menu'))
    return builder.as_markup()
