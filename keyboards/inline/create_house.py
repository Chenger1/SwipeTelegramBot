from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.callbacks.user_callback import POST_FILTER_CB, get_detail_callback_with_page

from middlewares import _

ITEM_CB = POST_FILTER_CB

tech_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Монолитный каркас с керамзитно-блочным заполнением'),
                         callback_data=ITEM_CB.new(action='add_tech',
                                                   value='MONO1')),
    InlineKeyboardButton(_('Монолитно-кирпичный'),
                         callback_data=ITEM_CB.new(action='add_tech',
                                                   value='MONO2')),
    InlineKeyboardButton(_('Монолитно-каркасный'),
                         callback_data=ITEM_CB.new(action='add_tech',
                                                   value='MONO3'))
).row(
    InlineKeyboardButton(_('Панельный'),
                         callback_data=ITEM_CB.new(action='add_tech',
                                                   value='PANEL')),
    InlineKeyboardButton(_('Пеноблок'),
                         callback_data=ITEM_CB.new(action='add_tech',
                                                   value='FOAM')),
    InlineKeyboardButton(_('Газобетон'),
                         callback_data=ITEM_CB.new(action='add_tech',
                                                   value='AREATED'))
)

terr_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Открытая'), callback_data=ITEM_CB.new(action='add_terr',
                                                                  value='OPEN')),
    InlineKeyboardButton(_('Закрытая'), callback_data=ITEM_CB.new(action='add_terr',
                                                                  value='CLOSE'))
)

payment_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Ипотека'), callback_data=ITEM_CB.new(action='add_payment',
                                                                 value='MORTGAGE')),
    InlineKeyboardButton(_('Материнский капитал'), callback_data=ITEM_CB.new(action='add_payment',
                                                                             value='CAPITAL')),
    InlineKeyboardButton(_('Прямая оплата'), callback_data=ITEM_CB.new(action='add_payment',
                                                                       value='PAYMENT'))
)

role_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Квартиры'), callback_data=ITEM_CB.new(action='add_role',
                                                                  value='FLAT')),
    InlineKeyboardButton(_('Офисы'), callback_data=ITEM_CB.new(action='add_role',
                                                               value='OFFICE'))
)

type_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Многоквартирный'), callback_data=ITEM_CB.new(action='add_type',
                                                                         value='MANY')),
    InlineKeyboardButton(_('Частный'), callback_data=ITEM_CB.new(action='add_type',
                                                                 value='ONE'))
).add(
    InlineKeyboardButton(_('Новострой'), callback_data=ITEM_CB.new(action='add_type',
                                                                   value='NOVOSTROY')),
    InlineKeyboardButton(_('Вторичный рынок'), callback_data=ITEM_CB.new(action='add_type',
                                                                         value='SECONDARY')),
    InlineKeyboardButton(_('Коттеджи'), callback_data=ITEM_CB.new(action='add_type',
                                                                  value='COTTAGES'))
)

house_class_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Обычный'), callback_data=ITEM_CB.new(action='add_house_class',
                                                                 value='COMMON')),
    InlineKeyboardButton(_('Элитный'), callback_data=ITEM_CB.new(action='add_house_class',
                                                                 value='ELITE'))
)

gas_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action='add_gas',
                                                             value='NO')),
    InlineKeyboardButton(_('Центрилизированный'), callback_data=ITEM_CB.new(action='add_gas',
                                                                            value='CENTER'))
)

heating_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action='add_heating',
                                                             value='NO')),
    InlineKeyboardButton(_('Центральное'), callback_data=ITEM_CB.new(action='add_heating',
                                                                     value='CENTER')),
    InlineKeyboardButton(_('Индивидуальное'), callback_data=ITEM_CB.new(action='add_heating',
                                                                        value='PERSONAL'))
)

electricity_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action='add_electricity',
                                                             value='NO')),
    InlineKeyboardButton(_('Подключено'), callback_data=ITEM_CB.new(action='add_electricity',
                                                                    value='YES'))
)

sewerage_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action='add_sewerage',
                                                             value='NO')),
    InlineKeyboardButton(_('Центральная'), callback_data=ITEM_CB.new(action='add_sewerage',
                                                                     value='CENTRAL')),
    InlineKeyboardButton(_('Индивидуальная'), callback_data=ITEM_CB.new(action='add_sewerage',
                                                                        value='PERSONAL'))
)

water_supply_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action='add_water',
                                                             value='NO')),
    InlineKeyboardButton(_('Центральное'), callback_data=ITEM_CB.new(action='add_water',
                                                                     value='CENTRAL')),
    InlineKeyboardButton(_('Индивидуальное'), callback_data=ITEM_CB.new(action='add_water',
                                                                        value='PERSONAL'))
)

confirm_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Да'), callback_data=ITEM_CB.new(action='create_confirm',
                                                            value=True)),
    InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action='create_confirm',
                                                             value=False))
)


async def get_advantages_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(_('Есть'), callback_data=ITEM_CB.new(action=action,
                                                                  value=True)),
        InlineKeyboardButton(_('Нет'), callback_data=ITEM_CB.new(action=action,
                                                                 value=False))
    )


#  Building, Section, Floor
async def get_building_keyboard(action: str, items: list, key: str, page: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for index, item in enumerate(items, start=1):
        markup.insert(InlineKeyboardButton(str(index), callback_data=get_detail_callback_with_page(action=action,
                                                                                                   pk=item['id'],
                                                                                                   key=key,
                                                                                                   page=page)))
    return markup
