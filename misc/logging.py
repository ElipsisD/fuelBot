"""Настройки логирования"""
import asyncio
import logging
import logging.config

from aiogram import Dispatcher


class TelegramHandler(logging.Handler):
    def __init__(self, dp, chat):
        logging.Handler.__init__(self)
        self.dp = dp
        self.chat = chat

    def emit(self, record):
        message = self.format(record)

        async def mes():
            await self.dp.bot.send_message(self.chat, message)

        loop = asyncio.get_event_loop()
        loop.create_task(mes())


def logger_config(dp: Dispatcher, logs_chat: int):
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
                'dp': dp,
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
