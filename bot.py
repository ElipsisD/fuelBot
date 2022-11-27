import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import load_config
from filters.filters_for_user import NewUser
from handlers.my_cars import register_user_my_cars
from handlers.new_ref import register_user_new_ref
from handlers.new_user import register_new_user
from handlers.stat import register_user_stat
from handlers.user import register_user

logger = logging.getLogger(__name__)


def register_all_middlewares(disp: Dispatcher):
    pass


def register_all_filters(disp: Dispatcher):
    disp.filters_factory.bind(NewUser)


def register_all_handlers(disp: Dispatcher):
    register_new_user(disp)
    register_user_new_ref(disp)
    register_user_my_cars(disp)
    register_user_stat(disp)
    register_user(disp)


logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

config = load_config('.env')
storage = MemoryStorage()  # RedisStorage2() is config.tg_bot.config.use_redis else MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)
bot['config'] = config

# register_all_middlewares(dp)
register_all_filters(dp)
register_all_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
