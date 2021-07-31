from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types

from utils.db_api.models import User

from typing import Tuple, Any, Optional


async def get_lang(user_id: int) -> str:
    user = await User.get_or_none(user_id=user_id)
    if user:
        return user.language


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user = types.User.get_current()
        return await get_lang(user.id) or user.locale
