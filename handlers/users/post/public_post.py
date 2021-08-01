import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.utils.exceptions import MessageNotModified

from loader import dp, Conn
from utils.session.url_dispatcher import REL_URLS
from deserializers.post import PostDeserializer

from middlewares import _

from keyboards.inline import user_keyboards
from keyboards.callbacks import user_callback

from typing import Union, Tuple, Coroutine

from utils.helpers import get_page
from utils.db_api.models import File

post_des = PostDeserializer()


async def get_post_list(page: str, message: Union[types.Message, types.CallbackQuery],
                        params: dict = None, data: dict = None) -> Tuple[str, Coroutine]:
    """ List of all posts """
    url = f'{REL_URLS["posts_public"]}?page={page}'
    resp = await Conn.get(url, user_id=message.from_user.id, params=params, data=data)
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
        return text, user_keyboards.get_keyboard_for_post(data, pages)
    else:
        return _('Публикаций нет'), user_keyboards.get_keyboard_for_post([], pages)


async def handle_posts(message: Union[types.Message, types.CallbackQuery], *args, **kwargs):
    text, keyboard_cor = await get_post_list(args[0], message)
    if isinstance(message, types.Message):
        await message.answer(text=_('Список публикаций'))
        await message.answer(text=text, reply_markup=await keyboard_cor)

    if isinstance(message, types.CallbackQuery):
        if kwargs.get('new'):
            await message.message.answer(text=text, reply_markup=await keyboard_cor)
        else:
            try:
                await message.message.edit_text(text=text, reply_markup=await keyboard_cor)
                await message.answer()
            except MessageNotModified:
                await message.answer(text='Больше публикаций нет', show_alert=True)


@dp.message_handler(Text(equals=['Список публикаций', 'List ads']))
async def public_post(message: types.Message):
    await handle_posts(message, '1')


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='post_list'))
async def post_list(call: types.CallbackQuery, callback_data: dict):
    page = callback_data.get('page')
    await handle_posts(call, page)


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='post_list_new'))
async def post_list(call: types.CallbackQuery, callback_data: dict):
    page = callback_data.get('page')
    await handle_posts(call, page, new=True)


@dp.callback_query_handler(user_callback.DETAIL_WITH_PAGE_CB.filter(action='post_detail'))
async def post_detail(call: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    page = callback_data.get('page')
    pk = callback_data['pk']
    url = f'{REL_URLS["posts_public"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    inst = await post_des.for_detail(resp)
    keyboard = await user_keyboards.get_keyboard_for_post_detail(page, pk,
                                                                 resp.get('flat_info')['id'])
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
    url = REL_URLS['like_dislike'].format(pk=pk)
    data = {'action': callback_data.get('type')}
    resp = await Conn.patch(url, data=data, user_id=call.from_user.id)

    url_detail = f'{REL_URLS["posts_public"]}{pk}/'
    resp_detail = await Conn.get(url_detail, user_id=call.from_user.id)
    inst = await post_des.for_detail(resp_detail)
    if resp.get('main_image'):
        pass
    page = callback_data.get('page')
    keyboard = await user_keyboards.get_keyboard_for_post_detail(page, pk,
                                                                 resp_detail.get('flat_info')['id'])
    await call.message.edit_caption(caption=inst.data, reply_markup=keyboard)
    await call.answer(text=_('Успешно'))
