from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from middlewares import _


starter_confirm = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(_('Подтвердить/Confirm'))
)


async def get_contact_button() -> ReplyKeyboardMarkup:
    contact_button = KeyboardButton(text=_('Отправить номер телефона'), request_contact=True)
    contact_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(contact_button)
    return contact_markup


async def get_skip_button() -> ReplyKeyboardMarkup:
    skip_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton(text=_('Пропустить'))
    )
    return skip_markup


remove_markup = ReplyKeyboardRemove()
