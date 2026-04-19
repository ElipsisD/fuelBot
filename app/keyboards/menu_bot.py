from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class RefuelingCallback(CallbackData, prefix="refueling"):
    level: str
    car: str = ""
    mode: str = ""
    odo: str = ""
    filing_volume: str = ""


menu_cd = RefuelingCallback


def make_callback_menu(level, car="", mode="", odo="", filing_volume=""):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return RefuelingCallback(
        level=level,
        car=car,
        mode=mode,
        odo=odo,
        filing_volume=filing_volume,
    ).pack()


menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='⛽НОВАЯ ЗАПРАВКА⛽',
        callback_data='new ref'
    )],
    [InlineKeyboardButton(
        text='📈СТАТИСТИКА📈',
        callback_data='stat'
    )],
    [InlineKeyboardButton(
        text='🔧ТО🔧',
        callback_data='maintenance'
    )],
    [InlineKeyboardButton(
        text='🔩НАСТРОЙКИ🔩',
        callback_data='settings'
    )],
    [InlineKeyboardButton(
        text='🚗ГАРАЖ🚗',
        callback_data='action menu cars'
    )],
    [InlineKeyboardButton(
        text='📱ОБРАТНАЯ СВЯЗЬ📱',
        url='https://t.me/bkdmitry',  # TODO сделать грамотный импорт из config
        switch_inline_query_current_chat='true'
    )]
])

back_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='↩назад',
        callback_data='menu'
    )]
])

for_new_user_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='🆕РЕГИСТРАЦИЯ🆕',
        callback_data='reg'
    )],
])
