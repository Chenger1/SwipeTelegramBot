from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks import user_callback

from typing import Iterable

from middlewares import _


lang_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Русский', callback_data=user_callback.LANG_CB.new(action='lang',
                                                                                 lang='ru')),
    InlineKeyboardButton(text='English', callback_data=user_callback.LANG_CB.new(action='lang',
                                                                                 lang='en'))
)


def get_detail_keyboard(action: str, title: str, pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(title, callback_data=user_callback.get_detail_callback(action, pk))
    )
    return markup


async def get_keyboard_for_post(items: Iterable, page: dict) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=4)
    for index, item in enumerate(items, start=1):
        markup.insert(
            InlineKeyboardButton(text=f'{index}',
                                 callback_data=user_callback.get_detail_callback(action='post_detail',
                                                                                 pk=item.pk))
        )
    markup.add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.get_list_callback(action='post_list',
                                                                                            page=page.get('prev'))),
        InlineKeyboardButton(text=_('На первую страницу'),
                             callback_data=user_callback.get_list_callback(action='post_list',
                                                                           page=page.get('first'))),
        InlineKeyboardButton(text=_('Вперед'), callback_data=user_callback.get_list_callback(action='post_list',
                                                                                             page=page.get('next')))
    )

    return markup
