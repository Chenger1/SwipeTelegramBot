from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.default.user_keyboards import get_user_keyboard


async def get_admin_keyboard() -> ReplyKeyboardMarkup:
    markup = await get_user_keyboard()
    markup.add(
        KeyboardButton('Панель администратора')
    )
    return markup


async def keyboard_dispatcher(is_admin: bool) -> ():
    """ Returns keyboard depends on user`s status """
    if is_admin:
        return await get_admin_keyboard()
    return await get_user_keyboard()
