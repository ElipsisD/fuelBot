from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from utils import db


class OnlyKeys(BoundFilter):
    async def check(selfs, message: types.Message) -> bool:
        return message.text in db.user_cars(str(message.from_user.id))


class NewUser(BoundFilter):
    async def check(selfs, message: types.Message) -> bool:
        return str(message.from_user.id) not in db.get_data()