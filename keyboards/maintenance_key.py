from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

maintenance_menu_cb = CallbackData('Maintenance', 'mode', 'car')


def make_callback_maintenance_menu(mode='', car=''):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return maintenance_menu_cb.new(mode=mode, car=car)


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
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=car,
                                  callback_data=make_callback_maintenance_menu(car=car, mode='car choice'))]
            for car in cars
        ],
    )
    markup.row(
        InlineKeyboardButton(text='↩назад', callback_data='menu')
    )
    return markup
