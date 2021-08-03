from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks.user_callback import POST_FILTER_CB

from middlewares import _


labels = {
    'BLANK': _('После ремонта'),
    'ROUGH': _('Черновая'),
    'EURO': _('Евроремонт'),
    'NEED': _('Требует ремонта'),
    'OPEN': _('Открытая'),
    'CLOSE': _('Закрытая'),
    'FREE': _('Свободная планировка'),
    'STUDIO': _('Студия'),
    'ADJACENT': _('Смежные комнаты'),
    'ISOLATED': _('Изолированные комнаты'),
    'SMALL': _('Малосемейки'),
    'ROOM': _('Гостинка')
}


async def get_filter_post_state_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('После ремонта'), callback_data=POST_FILTER_CB.new(action='filter_state',
                                                                                       value='BLANK')),
        InlineKeyboardButton(text=_('Черновая'), callback_data=POST_FILTER_CB.new(action='filter_state',
                                                                                  value='ROUGH'))
    ).add(
        InlineKeyboardButton(text=_('Евроремонт'), callback_data=POST_FILTER_CB.new(action='filter_state',
                                                                                    value='EURO')),
        InlineKeyboardButton(text=_('Требует ремонта'), callback_data=POST_FILTER_CB.new(action='filter_state',
                                                                                         value='NEED'))
    )
    return markup


async def get_filter_post_territory_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Открытая'), callback_data=POST_FILTER_CB.new(action='filter_territory',
                                                                                  value='OPEN')),
        InlineKeyboardButton(text=_('Закрытая'), callback_data=POST_FILTER_CB.new(action='filter_territory',
                                                                                  value='CLOSE'))
    )
    return markup


async def get_filter_post_plan_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Свободная планировка'), callback_data=POST_FILTER_CB.new(action='filter_plan',
                                                                                              value='FREE')),
        InlineKeyboardButton(text=_('Студия'), callback_data=POST_FILTER_CB.new(action='filter_plan',
                                                                                value='STUDIO'))
    ).add(
        InlineKeyboardButton(text=_('Смежные комнаты'), callback_data=POST_FILTER_CB.new(action='filter_plan',
                                                                                         value='ADJACENT')),
        InlineKeyboardButton(text=_('Изолированные комнаты'), callback_data=POST_FILTER_CB.new(action='filter_plan',
                                                                                               value='ISOLATED'))
    ).add(
        InlineKeyboardButton(text=_('Малосемейка'), callback_data=POST_FILTER_CB.new(action='filter_plan',
                                                                                     value='SMALL')),
        InlineKeyboardButton(text=_('Гостинка'), callback_data=POST_FILTER_CB.new(action='filter_plan',
                                                                                  value='ROOM'))
    )
    return markup


async def get_filter_post_confirm_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Подтверждаю'), callback_data=POST_FILTER_CB.new(action='filter_confirm',
                                                                                     value='YES')),
        InlineKeyboardButton(text=_('Ещё подумаю'), callback_data=POST_FILTER_CB.new(action='filter_confirm',
                                                                                     value='NO'))
    )
    return markup
