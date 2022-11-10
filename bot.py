import logging
import os
import time

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram import Bot, Dispatcher, executor

from handlers.user import register_user

API_TOKEN = os.getenv('API_TOKEN')


def register_all_handlers(dp: Dispatcher):
    register_user(dp)


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

register_all_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

