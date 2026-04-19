from typing import Any

from aiogram.filters import BaseFilter

from app.db import new_user_check


class NewUser(BaseFilter):
    async def __call__(self, event: Any) -> bool:
        from_user = getattr(event, "from_user", None)
        return from_user is not None and new_user_check(str(from_user.id))
