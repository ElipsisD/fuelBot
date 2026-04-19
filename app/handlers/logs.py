"""Работа с разделом ЛОГАМИ"""
from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

router = Router(name="logs")


@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def echo_message(m: Message):
    """ЭХО"""
    # await m.answer(m.chat.id)
    await m.bot.send_message(m.chat.id, m.text)
