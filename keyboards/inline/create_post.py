from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks import user_callback

from typing import Iterable

from middlewares import _


ITEM_CB = user_callback.POST_FILTER_CB


async def get_item_for_create_post(items: Iterable, action: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    for index, item in enumerate(items, start=1):
        markup.insert(InlineKeyboardButton(str(index),
                                           callback_data=user_callback.get_detail_callback(action=action,
                                                                                           pk=item.pk)))

    return markup


async def get_payment_options() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(_('Ипотека'), callback_data=ITEM_CB.new(action='add_payment',
                                                                            value='MORTGAGE'))
               ).add(
        InlineKeyboardButton(_('Пряма оплата'), callback_data=ITEM_CB.new(action='add_payment',
                                                                          value='PAYMENT'))
    ).row(
        InlineKeyboardButton(_('Материнский капитал'), callback_data=ITEM_CB.new(action='add_payment',
                                                                                 value='CAPITAL'))
    )
    return markup


async def get_communication_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(_('Звонок'), callback_data=ITEM_CB.new(action='add_comm',
                                                                           value='CALL'))
               ).add(
        InlineKeyboardButton(_('Сообщение'), callback_data=ITEM_CB.new(action='add_comm',
                                                                       value='MESSAGE'))
    ).row(
        InlineKeyboardButton(_('Звонок + сообщение'), callback_data=ITEM_CB.new(action='add_comm',
                                                                                value='BOTH'))
    )
    return markup


async def get_create_post_confirm_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Подтверждаю'), callback_data=ITEM_CB.new(action='create_confirm',
                                                                                     value='YES')),
        InlineKeyboardButton(text=_('Ещё подумаю'), callback_data=ITEM_CB.new(action='create_confirm',
                                                                                     value='NO'))
    )
    return markup
