from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData

import emoji

DETAIL_CB = CallbackData('detail', 'action', 'pk')
LIST_CB = CallbackData('list', 'action', 'pk')
COMPLAINT_CB = CallbackData('complaint', 'action', 'pk', 'type')

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


async def get_house_detail_keyboard(pk: int) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Новости дома', callback_data=LIST_CB.new(action='news_list', pk=pk)),
        InlineKeyboardButton('Документы', callback_data=LIST_CB.new(action='documents_list', pk=pk))
    )
    return inline_markup


async def get_post_detail_keyboard(post_pk: int, flat_pk: int) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup().row(
        InlineKeyboardButton('Подробнее о квартире',
                             callback_data=DETAIL_CB.new(action='flat_detail',
                                                         pk=flat_pk))
    ).add(
        InlineKeyboardButton(emoji.emojize(':thumbs_up:'), callback_data=DETAIL_CB.new(action='like_post', pk=post_pk)),
        InlineKeyboardButton(emoji.emojize(':thumbs_down:'), callback_data=DETAIL_CB.new(action='dislike_post',
                                                                                         pk=post_pk))
    ).row(
        InlineKeyboardButton('В избранное', callback_data=DETAIL_CB.new(action='save_to_favorites', pk=post_pk)),
        InlineKeyboardButton('Пожаловаться', callback_data=COMPLAINT_CB.new(action='complaint', pk=post_pk,
                                                                            type='_'))
    )
    return inline_markup


async def get_post_complaint_types(post_pk: int) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup().row(
        InlineKeyboardButton('Неккоректная цена', callback_data=COMPLAINT_CB.new(action='complaint',
                                                                                 pk=post_pk,
                                                                                 type='PRICE'))
    ).row(
        InlineKeyboardButton('Неккоректное фото', callback_data=COMPLAINT_CB.new(action='complaint',
                                                                                 pk=post_pk,
                                                                                 type='PHOTO'))
    ).row(
        InlineKeyboardButton('Неккоректное описание', callback_data=COMPLAINT_CB.new(action='complaint',
                                                                                     pk=post_pk,
                                                                                     type='DESC'))
    )
    return inline_markup
