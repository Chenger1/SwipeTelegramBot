from dataclasses import dataclass

from aiogram import types
from aiogram.dispatcher.filters.filters import BoundFilter

from utils.db_api.models import User


@dataclass
class IsAdmin(BoundFilter):
    key = 'is_admin'
    is_admin: bool

    async def check(self, message: types.Message) -> bool:
        user = await User.get(user_id=message.from_user.id)
        return user.is_admin
