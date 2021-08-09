from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks.user_callback import POST_FILTER_CB, get_detail_callback_with_page

from middlewares import _

ITEM_CB = POST_FILTER_CB


state_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('После ремонта'), callback_data=ITEM_CB.new(action='add_state',
                                                                       value='BLANK')),
    InlineKeyboardButton(_('Черновая'), callback_data=ITEM_CB.new(action='add_state',
                                                               value='ROUGH')),
    InlineKeyboardButton(_('Евроремонт'), callback_data=ITEM_CB.new(action='add_state',
                                                                    value='EURO')),
    InlineKeyboardButton(_('Требуте ремонта'), callback_data=ITEM_CB.new(action='add_state',
                                                                         value='NEED'))
)


foundation_doc_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Собственность'), callback_data=ITEM_CB.new(action='add_doc',
                                                                       value='OWNER')),
    InlineKeyboardButton(_('Аренда'), callback_data=ITEM_CB.new(action='add_doc',
                                                                value='RENT'))
)


plan_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Свободная планировка'), callback_data=ITEM_CB.new(action='add_plan',
                                                                              value='FREE')),
    InlineKeyboardButton(_('Студия'), callback_data=ITEM_CB.new(action='add_plan',
                                                                value='STUDIO')),
    InlineKeyboardButton(_('Смежные комнаты'), callback_data=ITEM_CB.new(action='add_plan',
                                                                         value='ADJACENT'))
).add(
    InlineKeyboardButton(_('Изолированные комнаты'), callback_data=ITEM_CB.new(action='add_plan',
                                                                               value='ISOLATED')),
    InlineKeyboardButton(_('Малосемейка'), callback_data=ITEM_CB.new(action='add_plan',
                                                                     value='SMALL')),
    InlineKeyboardButton(_('Гостинка'), callback_data=ITEM_CB.new(action='add_plan',
                                                                  value='ROOM'))
)


balcony_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Есть'), callback_data=ITEM_CB.new(action='add_balcony',
                                                              value='YES')),
    InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action='add_balcony',
                                                             value='NO'))
)


flat_type_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Апартаменты'), callback_data=ITEM_CB.new(action='add_type',
                                                                     value='FLAT')),
    InlineKeyboardButton(_('Офис'), callback_data=ITEM_CB.new(action='add_type',
                                                              value='OFFICE')),
    InlineKeyboardButton(_('Студия'), callback_data=ITEM_CB.new(action='add_type',
                                                                value='STUDIO'))
)


async def get_floors_keyboard(items: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for index, item in enumerate(items, start=1):
        markup.insert(
            InlineKeyboardButton(str(index), callback_data=ITEM_CB.new(action='add_floor',
                                                                       value=item['id']))
        )
    return markup
