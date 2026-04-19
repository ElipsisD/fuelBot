import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import load_config
from app.handlers.maintenance import router as maintenance_router
from app.handlers.my_cars import router as my_cars_router
from app.handlers.new_ref import router as new_ref_router
from app.handlers.new_user import router as new_user_router
from app.handlers.settings import router as settings_router
from app.handlers.stat import router as stat_router
from app.handlers.user import router as user_router
from app.misc.logging import logger_config
from app.db import init_db

ROUTERS = (
    new_user_router,
    new_ref_router,
    my_cars_router,
    stat_router,
    maintenance_router,
    settings_router,
    user_router,
)


logger = logging.getLogger("console_logger")


async def on_startup(bot: Bot, logs_chat):
    await bot.send_message(logs_chat, 'Бот запущен!')


def register_all_handlers(disp: Dispatcher):
    for router in ROUTERS:
        disp.include_router(router)


async def main():
    init_db()
    config = load_config()

    storage = MemoryStorage()
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)
    logging.config.dictConfig(logger_config(bot, config.tg_bot.logs_chat))

    register_all_handlers(dp)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await on_startup(bot, config.tg_bot.logs_chat)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
