from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn, log
from utils.session.url_dispatcher import REL_URLS
from deserializers.post import PostDeserializer

from middlewares import _

from keyboards.callbacks import user_callback
from keyboards.default.dispatcher import dispatcher
from keyboards.inline.user_keyboards import get_keyboard_for_list

from handlers.users.post.public_post import get_post
from handlers.users.utils import handle_list


post_des = PostDeserializer()


@dp.message_handler(Text(equals=['Мои объявления', 'My ads']))
async def my_posts(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_POSTS', message.from_user.id)
    await message.answer(_('Список моих публикаций'), reply_markup=keyboard)
    await handle_list(message, page='1', key='posts', keyboard=get_keyboard_for_list, detail_action='my_post_detail',
                      list_action='my_post_list', deserializer=post_des)
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
        await handle_list(call, page=page, key=key, keyboard=get_keyboard_for_list,
                          detail_action='my_post_detail', list_action='my_post_list', deserializer=post_des,
                          new_callback_answer=True)
    else:
        log.error(resp)
        await call.answer(_('Произошла ошибка. Попробуйте снова'))


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='my_post_list'))
async def post_list(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_list(call, page=page, key=key, params=params, deserializer=post_des, detail_action='my_post_detail',
                      list_action='my_post_list', keyboard=get_keyboard_for_list)


@dp.callback_query_handler(user_callback.LIST_CB.filter(action='my_post_list_new'))
async def post_list(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_list(call, page=page, key=key, params=params, deserializer=post_des, detail_action='my_post_detail',
                      list_action='my_post_list', new_callback_answer=True, keyboard=get_keyboard_for_list)
