import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import load_config
from filters.filters_for_user import NewUser
from handlers.logs import register_logs
from handlers.maintenance import register_user_maintenance
from handlers.my_cars import register_user_my_cars
from handlers.new_ref import register_user_new_ref
from handlers.new_user import register_new_user
from handlers.settings import register_user_settings
from handlers.stat import register_user_stat
from handlers.user import register_user
from misc.logging import logger_config


async def on_startup(bot: Bot, logs_chat):
    await bot.send_message(logs_chat, 'Бот запущен!')


def register_all_middlewares(disp: Dispatcher):
    pass


def register_all_filters(disp: Dispatcher):
    disp.filters_factory.bind(NewUser)


def register_all_handlers(disp: Dispatcher):
    register_user_maintenance(disp)
    register_new_user(disp)
    register_user_new_ref(disp)
    register_user_my_cars(disp)
    register_user_stat(disp)
    register_user_settings(disp)
    register_logs(disp)
    register_user(disp)


async def schedule(bot: Bot, logs_chat):
    await bot.send_message(logs_chat, 'Работа выполнена в определенный срок')


async def main():
    config = load_config('.env')

    storage = MemoryStorage()  # RedisStorage2() is config.tg_bot.config.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    bot['config'] = config
    logging.config.dictConfig(logger_config(dp, config.tg_bot.logs_chat))
    logger = logging.getLogger('console_logger')

    # register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await on_startup(bot, config.tg_bot.logs_chat)
        await dp.skip_updates()
        await bot.get_session()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await bot.get_session()
        await session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
