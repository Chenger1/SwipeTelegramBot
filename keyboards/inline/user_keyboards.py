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


async def get_keyboard_for_list(items: Iterable, pages: dict, key: str,
                                detail_action: str, list_action: str, **kwargs) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=4)
    for index, item in enumerate(items, start=1):
        markup.insert(
            InlineKeyboardButton(text=f'{index}',
                                 callback_data=user_callback.get_detail_callback_with_page(action=detail_action,
                                                                                           pk=item.pk,
                                                                                           page=pages.get('current'),
                                                                                           key=key))
        )
    markup.add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.get_list_callback(action=list_action,
                                                                                            page=pages.get('prev'),
                                                                                            key=key)),
        InlineKeyboardButton(text=_('Новое'),
                             callback_data=user_callback.get_list_callback(action=list_action,
                                                                           page=pages.get('first'),
                                                                           key=key)),
        InlineKeyboardButton(text=_('Вперед'), callback_data=user_callback.get_list_callback(action=list_action,
                                                                                             page=pages.get('next'),
                                                                                             key=key))
    )

    return markup


async def get_keyboard_for_post_detail(page: str, pk: int, flat_pk: int, key: str,
                                       user_id: int = None, favorites: list = None) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('О квартире'),
                             callback_data=user_callback.get_detail_callback(action='flat_detail',
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
            InlineKeyboardButton(_('Пожаловаться'),
                                 callback_data=user_callback.COMPLAINT_CB.new(action='complaint', pk=pk,
                                                                              type='_'))
        )
        if user_id in favorites:
            markup.insert(InlineKeyboardButton(_('Убрать из избранного'),
                                               callback_data=user_callback.get_detail_callback_with_page(
                                                   action='delete_from_favorites',
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
            InlineKeyboardButton(_('Пожаловаться'), callback_data=user_callback.COMPLAINT_CB.new(action='complaint',
                                                                                                 pk=pk,
                                                                                                 type='_'))
        ).row(
            InlineKeyboardButton(_('Убрать из избранного'),
                                 callback_data=user_callback.get_detail_callback_with_page(
                                     action='delete_from_favorites',
                                     pk=pk,
                                     key=key,
                                     page=page))
        )
    return markup


async def get_post_complaint_types(post_pk: int) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup().row(
        InlineKeyboardButton(_('Неккоректная цена'), callback_data=user_callback.COMPLAINT_CB.new(action='complaint',
                                                                                                  pk=post_pk,
                                                                                                  type='PRICE'))
    ).row(
        InlineKeyboardButton(_('Неккоректное фото'), callback_data=user_callback.COMPLAINT_CB.new(action='complaint',
                                                                                                  pk=post_pk,
                                                                                                  type='PHOTO'))
    ).row(
        InlineKeyboardButton(_('Неккоректное описание'),
                             callback_data=user_callback.COMPLAINT_CB.new(action='complaint',
                                                                          pk=post_pk,
                                                                          type='DESC'))
    )
    return inline_markup


async def get_keyboard_for_filter(items: Iterable) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=4)
    for index, item in enumerate(items, start=1):
        markup.insert(
            InlineKeyboardButton(text=f'{index}',
                                 callback_data=user_callback.get_detail_callback(action='filter_detail',
                                                                                 pk=item.pk))
        )

    return markup


async def get_keyboard_for_filter_detail(pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(_('Назад'), callback_data=user_callback.get_list_callback(action='filter_list',
                                                                                       page='1',
                                                                                       key='filter_list_new')),
        InlineKeyboardButton(_('Применить'), callback_data=user_callback.get_detail_callback(action='set_filter',
                                                                                             pk=pk))
    ).add(
        InlineKeyboardButton(_('Удалить'), callback_data=user_callback.get_detail_callback(action='delete_filter',
                                                                                           pk=pk))
    )
    return markup


async def get_keyboard_for_my_post_detail(page: str, pk: int, flat_pk: int, key: str, ) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('О квартире'),
                             callback_data=user_callback.get_detail_callback(action='flat_detail',
                                                                             pk=flat_pk))
    )
    markup.row(
        InlineKeyboardButton(_('Назад'), callback_data=user_callback.get_list_callback(action='my_post_list_new',
                                                                                       page=page,
                                                                                       key=key)),
        InlineKeyboardButton(_('Редактировать'), callback_data=user_callback.get_detail_callback(action='edit_post',
                                                                                                 pk=pk)),
        InlineKeyboardButton(_('Удалить'),
                             callback_data=user_callback.get_detail_callback_with_page(action='delete_post',
                                                                                       page=page,
                                                                                       key=key,
                                                                                       pk=pk))
    )
    return markup


async def get_keyboard_for_house(key: str, page: str, action: str, pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Квартиры'), callback_data=user_callback.LIST_CB_WITH_PK.new(action='flats_list',
                                                                                                 page='1',
                                                                                                 key='flats',
                                                                                                 pk=pk))
    ).add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.get_list_callback(action=action,
                                                                                            page=page,
                                                                                            key=key))
    )
    return markup


async def get_keyboard_for_my_house(key: str, page: str, action: str, pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Редактировать'),
                             callback_data=user_callback.get_detail_callback(action='edit_house',
                                                                             pk=pk)),
        InlineKeyboardButton(text=_('Удалить'), callback_data=user_callback.get_detail_callback(action='delete_house',
                                                                                                pk=pk))
    ).add(
        InlineKeyboardButton(_('Добавить корпус'),
                             callback_data=user_callback.get_detail_callback_with_page(action='add_building',
                                                                                       pk=pk,
                                                                                       key=key,
                                                                                       page=page)),
        InlineKeyboardButton(_('Добавить секцию'),
                             callback_data=user_callback.get_detail_callback_with_page(action='add_section',
                                                                                       pk=pk,
                                                                                       key=key,
                                                                                       page=page)),
        InlineKeyboardButton(_('Добавить этаж'),
                             callback_data=user_callback.get_detail_callback_with_page(action='add_floor',
                                                                                       pk=pk,
                                                                                       key=key,
                                                                                       page=page))
    ).add(
        InlineKeyboardButton(_('Корпуса'),
                             callback_data=user_callback.LIST_CB_WITH_PK.new(action='house_structure_list',
                                                                             page='1',
                                                                             key='buildings',
                                                                             pk=pk)),
        InlineKeyboardButton(_('Секции'), callback_data=user_callback.LIST_CB_WITH_PK.new(action='house_structure_list',
                                                                                          page='1',
                                                                                          key='sections',
                                                                                          pk=pk)),
        InlineKeyboardButton(_('Этажи'), callback_data=user_callback.LIST_CB_WITH_PK.new(action='house_structure_list',
                                                                                         page='1',
                                                                                         key='floors',
                                                                                         pk=pk))
    ).add(
        InlineKeyboardButton(text=_('Квартиры'), callback_data=user_callback.LIST_CB_WITH_PK.new(action='flats_list',
                                                                                                 page='1',
                                                                                                 key='flats',
                                                                                                 pk=pk)),
        InlineKeyboardButton(_('Добавить квартиру'), callback_data=user_callback.get_detail_callback(action='add_flat',
                                                                                                     pk=pk))
    ).add(
        InlineKeyboardButton(_('Новости'), callback_data=user_callback.LIST_CB_WITH_PK.new(action='news_list',
                                                                                           page='1',
                                                                                           key='news',
                                                                                           pk=pk)),
        InlineKeyboardButton(_('Добавить новость'), callback_data=user_callback.get_detail_callback(action='add_news',
                                                                                                    pk=pk))
    ).add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.get_list_callback(action=action,
                                                                                            page=page,
                                                                                            key=key))
    )
    return markup


async def get_keyboard_for_flat(key: str, page: str, action: str, pk: int,
                                house_pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Забронировать'),
                             callback_data=user_callback.get_detail_callback(action='booking_flat',
                                                                             pk=pk))
    ).add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.LIST_CB_WITH_PK.new(action=action,
                                                                                              page=page,
                                                                                              key=key,
                                                                                              pk=house_pk))
    )
    return markup


async def get_keyboard_for_flat_list(items: Iterable, pages: dict, key: str,
                                     detail_action: str, list_action: str, pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=4)
    for index, item in enumerate(items, start=1):
        markup.insert(
            InlineKeyboardButton(text=f'{index}',
                                 callback_data=user_callback.get_detail_callback_with_page(action=detail_action,
                                                                                           pk=item.pk,
                                                                                           page=pages.get('current'),
                                                                                           key=key))
        )
    markup.add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.LIST_CB_WITH_PK.new(action=list_action,
                                                                                              page=pages.get('prev'),
                                                                                              key=key,
                                                                                              pk=pk)),
        InlineKeyboardButton(text=_('Новое'),
                             callback_data=user_callback.LIST_CB_WITH_PK.new(action=list_action,
                                                                             page=pages.get('first'),
                                                                             key=key,
                                                                             pk=pk)),
        InlineKeyboardButton(text=_('Вперед'), callback_data=user_callback.LIST_CB_WITH_PK.new(action=list_action,
                                                                                               page=pages.get('next'),
                                                                                               key=key,
                                                                                               pk=pk))
    )

    return markup


async def get_keyboard_for_my_flat(key: str, page: str, action: str, pk: int, house_pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(_('Редактировать'), callback_data=user_callback.get_detail_callback(action='edit_flat',
                                                                                                 pk=pk))
    ).add(
        InlineKeyboardButton(_('Удалить'), callback_data=user_callback.get_detail_callback(action='delete_flat',
                                                                                           pk=pk))
    ).add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.LIST_CB_WITH_PK.new(action=action,
                                                                                              page=page,
                                                                                              key=key,
                                                                                              pk=house_pk))
    )
    return markup


async def get_keyboard_for_booked_flat(key: str, page: str, action: str, pk: int,
                                       house_pk: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Отменить бронь'),
                             callback_data=user_callback.get_detail_callback(action='unbooking_flat',
                                                                             pk=pk)),
        InlineKeyboardButton(text=_('Дом'),
                             callback_data=user_callback.get_detail_callback_with_page(action='from_flat_house_detail',
                                                                                       pk=house_pk,
                                                                                       page=page,
                                                                                       key=key))
    ).add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.LIST_CB_WITH_PK.new(action=action,
                                                                                              page=page,
                                                                                              key=key,
                                                                                              pk=house_pk))
    )
    return markup


async def get_keyboard_for_flat_detail_house(key: str, page: str, action: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text=_('Назад'), callback_data=user_callback.LIST_CB_WITH_PK.new(action=action,
                                                                                              page=page,
                                                                                              key=key,
                                                                                              pk='1'))
    )
    return markup


edit_user_role_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(_('Клиент'), callback_data=user_callback.POST_FILTER_CB.new(action='edit_role',
                                                                                     value='USER')),
    InlineKeyboardButton(_('Агент'), callback_data=user_callback.POST_FILTER_CB.new(action='edit_role',
                                                                                    value='AGENT')),
    InlineKeyboardButton(_('Нотариус'), callback_data=user_callback.POST_FILTER_CB.new(action='edit_role',
                                                                                       value='NOTARY')),
    InlineKeyboardButton(_('Отдел продаж'), callback_data=user_callback.POST_FILTER_CB.new(action='edit_role',
                                                                                           value='DEPART')),
)
