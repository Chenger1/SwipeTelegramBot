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

post_des = PostDeserializer()


async def get_post_list(page: str, message: Union[types.Message, types.CallbackQuery],
                        params: dict = None, data: dict = None) -> Tuple[str, Coroutine]:
    """ List of all posts """
    resp = await Conn.get(page, user_id=message.from_user.id, params=params, data=data)
    pages = {
        'next': resp.get('next') or f'{REL_URLS["posts_public"]}?page=last',
        'prev': resp.get('previous') or f'{REL_URLS["posts_public"]}?page=1',
        'first': f'{REL_URLS["posts_public"]}?page=1'
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
        try:
            await message.message.edit_text(text=text, reply_markup=await keyboard_cor)
            await message.answer()
        except MessageNotModified:
            await message.answer(text='Больше публикаций нет', show_alert=True)
            # await message.bot.answer_callback_query(callback_query_id=message.from_user.id,
            #                                         )


@dp.message_handler(Text(equals=['Список публикаций', 'List ads']))
async def public_post(message: types.Message):
    url = f'{REL_URLS["posts_public"]}?page=1'
    await handle_posts(message, url)


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='post_list'))
async def post_detail(call: types.CallbackQuery, callback_data: dict):
    page = callback_data.get('page')
    await handle_posts(call, page)
