from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks import user_callback

from typing import Iterable

from middlewares import _

import emoji


lang_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Русский', callback_data=user_callback.LANG_CB.new(action='lang',
                                                                                 lang='ru')),
    InlineKeyboardButton(text='English', callback_data=user_callback.LANG_CB.new(action='lang',
                                                                                 lang='en'))
)


async def get_detail_keyboard(action: str, title: str, pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(title, callback_data=user_callback.get_detail_callback(action, pk))
    )
    return markup


async def get_keyboard_for_post(items: Iterable, pages: dict, key: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=4)
    for index, item in enumerate(items, start=1):
        markup.insert(
            InlineKeyboardButton(text=f'{index}',
                                 callback_data=user_callback.get_detail_callback_with_page(action='post_detail',
                                                                                           pk=item.pk,
                                                                                           page=pages.get('current'),
                                                                                           key=key))
        )
    markup.add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.get_list_callback(action='post_list',
                                                                                            page=pages.get('prev'),
                                                                                            key=key)),
        InlineKeyboardButton(text=_('Новое'),
                             callback_data=user_callback.get_list_callback(action='post_list',
                                                                           page=pages.get('first'),
                                                                           key=key)),
        InlineKeyboardButton(text=_('Вперед'), callback_data=user_callback.get_list_callback(action='post_list',
                                                                                             page=pages.get('next'),
                                                                                             key=key))
    )

    return markup


async def get_keyboard_for_post_detail(page: str, pk: int, flat_pk: int, key: str,
                                       user_id: int = None, favorites: list = None) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('О квартире'),
                             callback_data=user_callback.get_detail_callback(action='post_detail',
                                                                             pk=flat_pk))
    ).add(
        InlineKeyboardButton(emoji.emojize(':thumbs_up:'),
                             callback_data=user_callback.LIKE_DISLIKE_CB.new(action='like_post',
                                                                             pk=pk,
                                                                             type='like',
                                                                             page=page,
                                                                             key=key)),
        InlineKeyboardButton(emoji.emojize(':thumbs_down:'),
                             callback_data=user_callback.LIKE_DISLIKE_CB.new(action='like_post',
                                                                             pk=pk,
                                                                             type='dislike',
                                                                             page=page,
                                                                             key=key))
    )
    if key == 'posts_public':
        markup.row(
                InlineKeyboardButton(_('Назад'), callback_data=user_callback.get_list_callback(action='post_list_new',
                                                                                               page=page,
                                                                                               key=key)),
                InlineKeyboardButton(_('Пожаловаться'), callback_data=user_callback.COMPLAINT_CB.new(action='complaint', pk=pk,
                                                                                                     type='_'))
                )
        if user_id in favorites:
            markup.insert(InlineKeyboardButton(_('Убрать из избранного'),
                                               callback_data=user_callback.get_detail_callback_with_page(action='delete_from_favorites',
                                                                                                         pk=pk,
                                                                                                         key=key,
                                                                                                         page=page)))
        else:
            markup.insert(InlineKeyboardButton(_('В избранное'),
                                               callback_data=user_callback.DETAIL_CB.new(action='save_to_favorites',
                                                                                         pk=pk)))
    elif key == 'favorites':
        markup.row(
                InlineKeyboardButton(_('Назад'), callback_data=user_callback.get_list_callback(action='post_list_new',
                                                                                               page=page,
                                                                                               key=key)),
                InlineKeyboardButton(_('Пожаловаться'), callback_data=user_callback.COMPLAINT_CB.new(action='complaint', pk=pk,
                                                                                                     type='_'))
                ).row(
                InlineKeyboardButton(_('Убрать из избранного'),
                                     callback_data=user_callback.get_detail_callback_with_page(action='delete_from_favorites',
                                                                                               pk=pk,
                                                                                               key=key,
                                                                                               page=page))
        )
    return markup
