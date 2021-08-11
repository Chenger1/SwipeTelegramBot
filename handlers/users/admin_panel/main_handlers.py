from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher
from keyboards.inline.user_keyboards import get_keyboard_for_list
from keyboards.callbacks.user_callback import LIST_CB
from deserializers.user import UserDeserializer

from middlewares import _

from utils.session.url_dispatcher import REL_URLS
from handlers.users.utils import handle_list

user_des = UserDeserializer()


@dp.message_handler(Text(equals=['Панель администратора', 'Admin Panel']), is_admin=True)
async def admin_panel(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_ADMIN_PANEL', message.from_user.id)
    await message.answer(_('Панель администратора'), reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Список нотариусов', 'Notary List']), is_admin=True)
async def notary_list(message: types.Message):
    resp = await Conn.get(REL_URLS['users'], params={'role': 'NOTARY'}, user_id=message.from_user.id)
    users = resp.get('results')
    if users:
        await handle_list(message, page='1', key='users', params={'role': 'NOTARY'},
                          deserializer=user_des, detail_action='user_notary_detail',
                          list_action='user_notary_list', keyboard=get_keyboard_for_list)
    else:
        await message.answer(_('Таких пользователей нет'))


@dp.callback_query_handler(LIST_CB.filter(action='user_notary_list'), is_admin=True)
async def notary_list_callback(call: types.CallbackQuery, callback_data: dict):
    page = callback_data.get('page')
    key = callback_data.get('key')
    await handle_list(call, page=page, key=key, params={'role': 'NOTARY'},
                      deserializer=user_des, detail_action='user_notary_detail',
                      list_action='user_notary_list', keyboard=get_keyboard_for_list)
