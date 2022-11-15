from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def cars_key(cars: list) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=car)] for car in cars
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
