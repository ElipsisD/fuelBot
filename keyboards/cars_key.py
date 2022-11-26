from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

actions_menu = CallbackData('Cars_cb', 'level', 'mode', 'car')


def make_callback_actions_menu(level, mode='', car=''):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return actions_menu.new(level=level,
                            mode=mode,
                            car=car)


actions_with_cars = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='🆕ДОБАВИТЬ АВТОМОБИЛЬ🆕',
        callback_data=make_callback_actions_menu(level='', mode='add car')
    )],
    [InlineKeyboardButton(
        text='🚮УДАЛИТЬ АВТОМОБИЛЬ🚮',
        callback_data=make_callback_actions_menu(level='', mode='delete car')
    )],
    [InlineKeyboardButton(
        text='↩назад',
        callback_data='menu'
    )]
])


def actions_cars_key(cars: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора автомобиля"""
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=car,
                                  callback_data=make_callback_actions_menu(level='', car=car, mode='choice'))]
            for car in cars
        ],
    )
    markup.row(
        InlineKeyboardButton(text='↩назад', callback_data='menu')
    )
    return markup
