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
        KeyboardButton(_('Текущие фильтры')),
        KeyboardButton(_('Мои фильтры')),
        KeyboardButton(_('Сбросить фильтры'))
    ).add(
        KeyboardButton(_('Добавить новую публикацию')),
        KeyboardButton(_('Мои публикации'))
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
        KeyboardButton(_('Вернуться')),
        KeyboardButton(_('Сохранить фильтр'))
    )
    return markup


async def get_level_3_create_post_keyboard(is_admin) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к дому')),
        KeyboardButton(_('Перейти к квартире'))
    ).add(
        KeyboardButton(_('Перейти к цене')),
        KeyboardButton(_('Перейти к способу платежа'))
    ).add(
        KeyboardButton(_('Перейти к вариантам связи'))
    ).add(
        KeyboardButton(_('Перейти к описанию')),
        KeyboardButton(_('Перейти к фото'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )
    return markup
