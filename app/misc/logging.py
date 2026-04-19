import asyncio
import logging
import logging.config

from aiogram import Bot


class TelegramHandler(logging.Handler):
    def __init__(self, bot: Bot, chat: int):
        logging.Handler.__init__(self)
        self.bot = bot
        self.chat = chat

    def emit(self, record):
        message = self.format(record)

        async def mes():
            await self.bot.send_message(self.chat, message)

        loop = asyncio.get_event_loop()
        loop.create_task(mes())


def logger_config(bot: Bot, logs_chat: int):
    return {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'std_format': {
                'format': '{asctime} - {levelname} - {name} - {message}',
                'style': '{'
            },
            'telegram_format': {
                'format': '{levelname} : {message}',
                'style': '{'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'std_format'
            },
            'chat': {
                '()': TelegramHandler,
                'bot': bot,
                'chat': logs_chat,
                'level': 'DEBUG',
                'formatter': 'telegram_format'
            }
        },
        'loggers': {
            'telegram_logger': {
                'level': 'DEBUG',
                'handlers': ['chat'],
                'propagate': False,
            },
            'console_logger': {
                'level': 'DEBUG',
                'handlers': ['console']
            }
        },
    }
