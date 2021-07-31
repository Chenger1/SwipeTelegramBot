from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def get_user_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('Список публикаций'),
        KeyboardButton('Список домов')
    )
    return markup
