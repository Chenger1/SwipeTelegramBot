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
        KeyboardButton(_('Фильтрация объявлений'))
    ).add(
        KeyboardButton(_('Текущие фильтры'))
    ).add(
        KeyboardButton(_('Сбросить фильтры'))
    )
    return markup


async def get_level_2_filter_post_keyboard(is_admin) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Фильтровать'))
    ).add(
        KeyboardButton(_('Перейти к цене'))
    ).add(
        KeyboardButton(_('Перейти к площади'))
    ).add(
        KeyboardButton(_('Перейти к городу'))
    ).add(
        KeyboardButton(_('Перейти к состоянию квартиры'))
    ).add(
        KeyboardButton(_('Перейти к планировке'))
    ).add(
        KeyboardButton(_('Перейти к территории'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )
    return markup
