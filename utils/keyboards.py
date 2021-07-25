from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData


DETAIL_CB = CallbackData('detail', 'action', 'pk')
LIST_CB = CallbackData('list', 'action', 'pk')


contact_button = KeyboardButton(text='Отправить номер телефона', request_contact=True)
contact_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(contact_button)
remove_reply = ReplyKeyboardRemove()


def get_detail_keyboard(pk: int, title: str, action: str) -> InlineKeyboardMarkup:
    """ Generate one button which includes primary key of object """
    inline_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(title,
                             callback_data=DETAIL_CB.new(action=action,
                                                         pk=pk))
    )
    return inline_markup


def get_house_keyboard(pk: int, ) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Подробнее о доме', callback_data=DETAIL_CB.new(action='house_detail', pk=pk)),
        InlineKeyboardButton('Список квартир', callback_data=LIST_CB.new(action='house_flats_list', pk=pk))
    )
    return inline_markup
