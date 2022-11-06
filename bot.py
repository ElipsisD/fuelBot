import logging
import os
import time

from aiogram import Bot, Dispatcher, executor, types

import exceptions
import refuelings

API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    logging.info(f'{message.from_user.id=} {message.from_user.username=} {time.asctime()}')
    await message.answer(f"Привет, {message.from_user.first_name}!\n\n"
                         f"Для корректных расчетов необходимо заправлять до полного бака\n"
                         f"Давай внесем данные о твоей последней заправке!\n"
                         f"Внеси данные в формате: объем_заправки_в_литрах общий_пробег\n"
                         f"Пример:\n48,21 125485")


@dp.message_handler()
async def add_refueling(message: types.Message):
    """Добавление данных о новой заправке"""
    try:
        refueling = refuelings.add_refueling(message)
    except exceptions.NotCorrectRefueling as e:
        await message.answer(str(e))
        return
    answer_message = (
        'Данные о заправке добавлены!\n'
    )
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
