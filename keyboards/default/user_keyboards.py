from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from middlewares import _


async def get_user_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Список публикаций')),
        KeyboardButton(_('Список домов'))
    ).row(
        KeyboardButton(_('Избранное'))
    ).row(
        KeyboardButton(_('Настройки'))
    )
    return markup


async def get_level_2_post_keyboard(is_admin) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Вернуться')),
    ).add(
        KeyboardButton(_('Фильтрация постов'))
    )
    return markup
