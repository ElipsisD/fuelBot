from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

new_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='НОВАЯ ЗАПРАВКА',
        callback_data='/new'
    )
    ]
])
