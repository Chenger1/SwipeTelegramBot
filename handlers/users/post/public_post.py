import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified, MessageTextIsEmpty

from loader import dp, Conn
from utils.session.url_dispatcher import REL_URLS
from deserializers.post import PostDeserializer, PostFilterDeserializer

from middlewares import _

from keyboards.inline import user_keyboards
from keyboards.callbacks import user_callback
from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline.filter_post import labels

from typing import Union, Tuple, Coroutine, Optional

from utils.helpers import get_page
from utils.db_api.models import File, User


post_des = PostDeserializer()
filter_des = PostFilterDeserializer()


async def prepare_dict(obj: Optional[dict]) -> dict:
    if obj:
        new_dict = {}
        for key, value in obj.items():
            if type(value) in (int, str):
                new_dict[key] = value
        return new_dict


async def get_post_list(page: str, message: Union[types.Message, types.CallbackQuery],
                        params: dict = None, data: dict = None,
                        key: str = None, **kwargs) -> Tuple[str, Coroutine]:
    """ List of all posts """
    # url = f'{REL_URLS["posts_public"]}?page={page}'
    url = f'{REL_URLS[key]}?page={page}'
    resp = await Conn.get(url, user_id=message.from_user.id, params=await prepare_dict(params),
                          data=await prepare_dict(data))
    pages = {
        'next': await get_page(resp.get('next')) or 'last',
        'prev': await get_page(resp.get('previous')) or '1',
        'first': '1',
        'current': page
    }
    if resp:
        data = await post_des.make_list(resp)
        text = ''
        for index, item in enumerate(data, start=1):
            text += f'{index}. {item.data}\n'
        return text, kwargs.get('custom_keyboard', user_keyboards.get_keyboard_for_post)(data, pages, key)
    else:
        return _('Публикаций нет'), kwargs.get('custom_keyboard', user_keyboards.get_keyboard_for_post)([], pages, key)


async def handle_posts(message: Union[types.Message, types.CallbackQuery], **kwargs):
    params = kwargs.get('params')
    if params and 'path' in params.keys():
        params.pop('path')
    text, keyboard_cor = await get_post_list(kwargs.get('page'), message, key=kwargs.get('key'),
                                             params=kwargs.get('params'), data=kwargs.get('data'))
    if isinstance(message, types.Message):
        if text:
            if kwargs.get('keyboard'):
                await message.answer(text=_('Список публикаций'), reply_markup=kwargs.get('keyboard'))
            else:
                await message.answer(text=_('Список публикаций'))
            await message.answer(text=text, reply_markup=await keyboard_cor)
        else:
            keyboard_cor.close()
            await message.answer(text=_('Публикаций нет'))

    if isinstance(message, types.CallbackQuery):
        if text:
            if kwargs.get('new'):
                await message.message.answer(text=_('Список публикаций'), reply_markup=kwargs.get('keyboard'))
                await message.message.answer(text=text, reply_markup=await keyboard_cor)
            else:
                try:
                    await message.message.edit_text(text=text, reply_markup=await keyboard_cor)
                    await message.answer()
                except MessageNotModified:
                    await message.answer(text='Больше публикаций нет', show_alert=True)
        else:
            keyboard_cor.close()
            await message.message.answer(text=_('Публикаций нет'))
            await message.answer()


async def get_filter_list(message: Union[types.Message, types.CallbackQuery]):
    resp = await Conn.get(REL_URLS['filters'], user_id=message.from_user.id)
    if resp:
        data = await filter_des.make_list(resp)
        text = ''
        for index, item in enumerate(data, start=1):
            text += f'{index}. {item.data}\n'
        return text, user_keyboards.get_keyboard_for_filter(data)
    else:
        return _('Фильтров нет'), user_keyboards.get_keyboard_for_filter([])


async def handle_filters(message: Union[types.Message, types.CallbackQuery]):
    text, keyboard_cor = await get_filter_list(message)
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=await keyboard_cor)
    elif isinstance(message, types.CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=await keyboard_cor)
        except (MessageTextIsEmpty, MessageNotModified):
            await message.message.edit_text(_('Фильтров нет'))
    else:
        keyboard_cor.close()


@dp.message_handler(Text(equals=['Текущие фильтры', 'Current filters']))
async def current_filters(message: types.Message, state: FSMContext):
    data = await state.get_data()
    no_data = _('Не указано')
    text = '<b>Цена</b> {price__gte}:{price__lte} грн\n' \
           '<b>Площадь</b> {square__gte}:{square__lte} м2\n' \
           '<b>Город</b>: {city}\n <b>Состояние</b> {state}\n' \
           '<b>Территория</b>: {terr}\n <b>Планировка</b> {plan}'. \
        format(price__gte=data.get('price__gte', no_data),
               price__lte=data.get('price__lte', no_data),
               square__gte=data.get('flat__square__gte', no_data),
               square__lte=data.get('flat__square__lte', no_data),
               city=data.get('house__city', no_data),
               state=labels.get(data.get('flat__state'), no_data),
               terr=labels.get(data.get('house__territory'), no_data),
               plan=labels.get(data.get('flat__plan'), no_data))
    await message.answer(_(text))


@dp.message_handler(Text(equals=['Сбросить фильтры', 'Current filters']))
async def current_filters(message: types.Message, state: FSMContext):
    data = await state.get_data()
    path = data.get('path')
    await state.reset_data()
    await state.update_data(path=path)
    await message.answer(_('Фильтры сброшены'))
    await handle_posts(message, page='1', key='posts_public')


@dp.message_handler(Text(equals=['Мои фильтры', 'My filters']))
async def user_filters(message: types.Message):
    await handle_filters(message)


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='filter_list'))
async def user_filters_callback(call: types.CallbackQuery, callback_data: dict):
    await handle_filters(call)


@dp.callback_query_handler(user_callback.DETAIL_CB.filter(action='filter_detail'))
async def filter_detail(call: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    url = f'{REL_URLS["filters"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    if resp:
        data = await filter_des.for_detail(resp)
        await call.message.edit_text(data.data, reply_markup=await user_keyboards.get_keyboard_for_filter_detail(pk))
        await call.answer()
    else:
        await call.answer(_('Фильтра не найден'), show_alert=True)


@dp.callback_query_handler(user_callback.DETAIL_CB.filter(action='set_filter'))
async def set_filter(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["filters"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    data = await state.get_data()
    for key, value in resp.items():
        if value and key not in ('name', 'saved_filter_pk'):
            data[key] = value
    await state.update_data(data)
    logging.info(data)
    await call.answer(_('Фильтр установлен'))


@dp.callback_query_handler(user_callback.DETAIL_CB.filter(action='delete_filter'))
async def delete_filter(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["filters"]}{pk}/'
    resp, status = await Conn.delete(url, user_id=call.from_user.id)
    if status == 204:
        await call.answer(_('Фильтр удален'), show_alert=True)
        await handle_filters(call)
    else:
        await call.answer(_('Произошла ошибка. Попробуйте снова'), show_alert=True)


@dp.message_handler(Text(equals=['Список публикаций', 'List ads']))
async def public_post(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_POSTS', message.from_user.id)
    params = await state.get_data()
    await handle_posts(message, page='1', key='posts_public', keyboard=keyboard,
                       params=params)
    await state.update_data(path=path)


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='post_list'))
async def post_list(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_posts(call, page=page, key=key, params=params)


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='post_list_new'))
async def post_list(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_posts(call, page=page, new=True, key=key, params=params)


@dp.callback_query_handler(user_callback.DETAIL_WITH_PAGE_CB.filter(action='post_detail'))
async def post_detail(call: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    page = callback_data.get('page')
    pk = callback_data['pk']
    key = callback_data.get('key')
    url = f'{REL_URLS["posts_public"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    inst = await post_des.for_detail(resp)
    user = await User.get(user_id=call.from_user.id)
    keyboard = await user_keyboards.get_keyboard_for_post_detail(page, pk,
                                                                 resp.get('flat_info')['id'],
                                                                 key=key,
                                                                 user_id=user.swipe_id,
                                                                 favorites=resp.get('in_favorites'))
    if resp.get('main_image'):
        file_path = resp.get('main_image')
        filename = file_path.split('/')[-1]
        file_data = await File.get_or_none(filename=filename, parent_id=pk)
        if not file_data:
            resp_file = await Conn.get(file_path, user_id=call.from_user.id)
            msg = await call.bot.send_photo(chat_id=call.from_user.id,
                                            photo=resp_file.get('file'), caption=inst.data,
                                            reply_markup=keyboard)
            await File.create(filename=filename, parent_id=pk,
                              file_id=msg.photo[-1].file_id)
        else:
            await call.bot.send_photo(chat_id=call.from_user.id,
                                      photo=file_data.file_id, caption=inst.data,
                                      reply_markup=keyboard)
    else:
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=_('Невалидная публикация. Пожалуйста, сообщите администрации'),
                                    reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(user_callback.LIKE_DISLIKE_CB.filter(action='like_post'))
async def list_post(call: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    key = callback_data.get('key')
    url = REL_URLS['like_dislike'].format(pk=pk)
    data = {'action': callback_data.get('type')}
    resp = await Conn.patch(url, data=data, user_id=call.from_user.id)

    url_detail = f'{REL_URLS["posts_public"]}{pk}/'
    resp_detail = await Conn.get(url_detail, user_id=call.from_user.id)
    inst = await post_des.for_detail(resp_detail)
    page = callback_data.get('page')
    keyboard = await user_keyboards.get_keyboard_for_post_detail(page, pk,
                                                                 resp_detail.get('flat_info')['id'],
                                                                 key=key,
                                                                 favorites=resp_detail.get('in_favorites'))
    await call.message.edit_caption(caption=inst.data, reply_markup=keyboard)
    await call.answer(text=_('Успешно'))


@dp.callback_query_handler(user_callback.DETAIL_CB.filter(action='save_to_favorites'))
async def save_to_favorites(call: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    resp, status = await Conn.post(REL_URLS['favorites'], data={'post': pk},
                                   user_id=call.from_user.id)
    if status == 201:
        await call.answer(text=_('Добавлено'), show_alert=True)
    elif status == 409:
        await call.answer(text=_('Это объявление уже в вашем списке избранного'),
                          show_alert=True)
    else:
        logging.error(resp)
        await call.answer(text=_('Произошла ошибка. Попробуйте еще раз'),
                          show_alert=True)


@dp.message_handler(Text(equals=['Избранное', 'Favorites']))
async def public_post(message: types.Message):
    await handle_posts(message, page='1', key='favorites')


@dp.callback_query_handler(user_callback.DETAIL_WITH_PAGE_CB.filter(action='delete_from_favorites'))
async def delete_from_favorites(call: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    page = callback_data['page']
    key = callback_data['key']
    url = f'{REL_URLS["favorites"]}{pk}/'
    resp, status = await Conn.delete(url, call.from_user.id)
    if status == 204:
        await handle_posts(call, page=page, key=key, new=True)
    else:
        logging.error(resp)
        await call.answer(_('Произошла ошибка. Попробуйте снова'))


@dp.callback_query_handler(user_callback.COMPLAINT_CB.filter(action='complaint'))
async def complaint(call: types.CallbackQuery, callback_data: dict):
    """
        If callback_data contains - 'type' key - uses this type to create new complaint.
        Otherwise, create inline keyboard with complaint types for user.
    """
    logging.info(callback_data)
    pk = callback_data['pk']
    if callback_data.get('type') != '_':
        resp, status = await Conn.post(REL_URLS['complaint'],
                                       data={'post': pk, 'type': callback_data.get('type')},
                                       user_id=call.from_user.id)
        if status == 201:
            await call.answer(_('Жалоба отправлена'), show_alert=True)
        elif status == 409:
            await call.answer(_('Вы уже отправили жалобу.'), show_alert=True)
        else:
            logging.error(resp)
            await call.answer(_('Произошла ошибка. Повторите попытку'))
    else:
        keyboard = await user_keyboards.get_post_complaint_types(post_pk=pk)
        await call.message.answer(text=_('Укажите причину жалобы'), reply_markup=keyboard)
        await call.answer()


@dp.message_handler(Text(equals=['Вернуться', 'Back']))
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    await state.update_data(path=path)
