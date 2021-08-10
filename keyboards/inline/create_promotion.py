from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks.user_callback import POST_FILTER_CB
from middlewares import _

ITEM_CB = POST_FILTER_CB


phrase_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Подарок при покупке'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                          value='GIFT')),
    InlineKeyboardButton(_('Возможен торг'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                       value='TRADE'))
    ).add(
    InlineKeyboardButton(_('Квартира у моря'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                         value='SEA')),
    InlineKeyboardButton(_('В спальном районе'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                           value='SLEEP'))
).add(
    InlineKeyboardButton(_('Вам повезло с ценой'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                             value='PRICE')),
    InlineKeyboardButton(_('Для большой семьи'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                           value='BIG_FAMILY'))
).add(
    InlineKeyboardButton(_('Семейное гнездышко'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                            value='FAMILY')),
    InlineKeyboardButton(_('Отдельная парковка'), callback_data=ITEM_CB.new(action='add_phrase',
                                                                            value='CAR_PARK'))
)


async def get_promotion_type_keyboard(items: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for item in items:
        markup.insert(
            InlineKeyboardButton(item['name'], callback_data=ITEM_CB.new(action='add_type',
                                                                         value=item['id']))
        )
    return markup
