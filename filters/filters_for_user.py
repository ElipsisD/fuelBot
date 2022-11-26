from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from utils import db


class NewUser(BoundFilter):
    async def check(selfs, message: types.Message) -> bool:
        return db.new_user_check(str(message.from_user.id))