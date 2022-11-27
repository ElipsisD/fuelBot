from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

stat_menu_cb = CallbackData('Stat', 'mode', 'car')


def make_callback_stat_menu(mode='', car=''):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return stat_menu_cb.new(mode=mode,
                            car=car)


def stat_menu(car: str):
    """Клавиатура вариантов статистики с информацией об автомобиле"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='◀ПОСЛЕДНЯЯ ЗАПРАВКА▶',
            callback_data=make_callback_stat_menu(mode='mode choice', car=car)
        )],
        [InlineKeyboardButton(
            text='↩назад',
            callback_data='menu'
        )]
    ])


def stat_cars_key(cars: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора автомобиля"""
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=car,
                                  callback_data=make_callback_stat_menu(car=car, mode='car choice'))]
            for car in cars
        ],
    )
    markup.row(
        InlineKeyboardButton(text='↩назад', callback_data='menu')
    )
    return markup
