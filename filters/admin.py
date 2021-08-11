from aiogram import types
from aiogram.dispatcher.filters.filters import BoundFilter

from utils.db_api.models import User

from typing import Union


class IsAdmin(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: Union[types.Message, types.CallbackQuery]) -> bool:
        user = await User.get(user_id=message.from_user.id)
        return user.is_admin
