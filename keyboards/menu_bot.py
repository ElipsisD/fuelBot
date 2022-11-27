from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

menu_cd = CallbackData('Refueling', 'level', 'car', 'mode', 'odo', 'filing_volume')


def make_callback_menu(level, car='', mode='', odo='', filing_volume=''):
    """Создание объекта CallbackData для хранения данных и отлавливания состояний"""
    return menu_cd.new(level=level,
                       car=car,
                       mode=mode,
                       odo=odo,
                       filing_volume=filing_volume)


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
        text='🆕РЕГИСТАРЦИЯ🆕',
        callback_data='reg'
    )],
])
