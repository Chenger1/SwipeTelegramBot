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
