from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


contact_button = KeyboardButton(text='Отправить номер телефона', request_contact=True)
contact_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(contact_button)

skip_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton(text='Пропустить')
)

remove_markup = ReplyKeyboardMarkup()
