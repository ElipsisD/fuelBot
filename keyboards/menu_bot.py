from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

menu_cd = CallbackData('Refueling', 'level', 'car', 'mode', 'odo', 'filing_volume')


def make_callback_data(level, car='', mode='', odo='', filing_volume=''):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return menu_cd.new(level=level,
                       car=car,
                       mode=mode,
                       odo=odo,
                       filing_volume=filing_volume)


menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='НОВАЯ ЗАПРАВКА',
        callback_data='new ref'
    )],
    [InlineKeyboardButton(
        text='СТАТИСТИКА',
        callback_data='stat'
    )],
    [InlineKeyboardButton(
        text='МОИ АВТОМОБИЛИ',
        callback_data='menu cars'
    )],
    [InlineKeyboardButton(
        text='СВЯЗАТЬСЯ С РАЗРАБОТЧИКОМ',
        callback_data='contact to admin'
    )]
])


def cars_key(cars: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора автомобиля для заправки"""
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=car, callback_data=make_callback_data(level='2', car=car))] for car in cars
        ],
    )
    markup.row(
        InlineKeyboardButton(text='назад', callback_data=make_callback_data(level='0'))
    )
    return markup


def refueling_mode(car: str) -> InlineKeyboardMarkup:
    """Меню выбора типа заправки (полный бак или частичная заправка)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='ПОЛНЫЙ БАК',
            callback_data=make_callback_data(level='3', car=car, mode='full')
        )],
        [InlineKeyboardButton(
            text='ЧАСТИЧНАЯ ЗАПРАВКА',
            callback_data=make_callback_data(level='3', car=car, mode='partial')
        )],
        [InlineKeyboardButton(
            text='назад',
            callback_data=make_callback_data(level='0')
        )]
    ])


back_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='назад',
        callback_data=make_callback_data(level='0')
    )]
])