import logging
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from filters.choice import OnlyKeys
from handlers.user import register_user

API_TOKEN = os.getenv('API_TOKEN')


def register_all_filters(disp: Dispatcher):
    disp.filters_factory.bind(OnlyKeys)


def register_all_handlers(disp: Dispatcher):
    register_user(disp)


logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

register_all_filters(dp)
register_all_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
