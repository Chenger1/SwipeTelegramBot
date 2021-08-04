import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn
from utils.session.url_dispatcher import REL_URLS
from deserializers.post import PostDeserializer

from middlewares import _

from keyboards.callbacks import user_callback
from keyboards.default.dispatcher import dispatcher

from handlers.users.post.public_post import handle_posts, get_post


post_des = PostDeserializer()


@dp.message_handler(Text(equals=['Мои публикации', 'My ads']))
async def my_posts(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_POSTS', message.from_user.id)
    await handle_posts(message, page='1', key='posts',
                       keyboard=keyboard, detail_action='my_post_detail')
    await state.update_data(path=path)


@dp.callback_query_handler(user_callback.DETAIL_WITH_PAGE_CB.filter(action='my_post_detail'))
async def my_post_detail(call: types.CallbackQuery, callback_data: dict):
    await get_post(call, callback_data, 'my_post_detail')


@dp.callback_query_handler(user_callback.DETAIL_WITH_PAGE_CB.filter(action='delete_post'))
async def delete_post(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data['pk']
    page = callback_data['page']
    key = callback_data['key']
    url = f'{REL_URLS["posts"]}{pk}/'
    resp, status = await Conn.delete(url, user_id=call.from_user.id)
    if status == 204:
        await handle_posts(call, page=page, key=key, detail_action='my_post_detail',
                           new=True)
    else:
        logging.error(resp)
        await call.answer(_('Произошла ошибка. Попробуйте снова'))
