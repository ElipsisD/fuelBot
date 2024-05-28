import logging
import os

import easyocr
from aiogram import types, Dispatcher

logger = logging.getLogger('telegram_logger')

reader = easyocr.Reader(['en', 'ru'])


async def check_photo(message: types.Message):
    # Получаем информацию о самой большой версии фотографии
    photo = message.photo[-1]
    # Получаем бинарные данные изображения
    photo_bytes = await photo.download()
    # Распознаем текст на изображении
    result = reader.readtext(photo_bytes.name)
    bot = message.bot
    chat_id = message.chat.id
    await message.delete()

    # Формируем ответ с распознанным текстом
    response = "\n".join([res[1] for res in result])
    # Отправляем ответ пользователю
    await bot.send_message(chat_id, response)

    photo_bytes.close()
    os.remove(photo_bytes.name)


def register_photo(dp: Dispatcher):
    """Регистрация хендлеров"""
    dp.register_message_handler(check_photo, content_types=['photo'])
