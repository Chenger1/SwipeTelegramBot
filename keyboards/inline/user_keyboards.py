from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks import user_callback


lang_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Русский', callback_data=user_callback.LANG_CB.new(action='lang',
                                                                                 lang='ru')),
    InlineKeyboardButton(text='English', callback_data=user_callback.LANG_CB.new(action='lang',
                                                                                 lang='en'))
)
