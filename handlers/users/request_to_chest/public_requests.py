import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text

from keyboards.inline.user_keyboards import get_keyboard_for_list
from loader import dp, Conn

from utils.session.url_dispatcher import REL_URLS

from handlers.users.utils import handle_list

from deserializers.house import RequestDeserializer

from keyboards.callbacks.user_callback import DETAIL_WITH_PAGE_CB, LIST_CB
from keyboards.inline.user_keyboards import get_keyboard_for_request_detail


request_des = RequestDeserializer()


keyboard_request_detail = {
    'request_detail': get_keyboard_for_request_detail
}


async def get_request(call: types.CallbackQuery, callback_data: dict, keyboard_key: str):
    keyboard_cor = keyboard_request_detail[keyboard_key]
    logging.info(callback_data)
    pk = callback_data.get('pk')
    url = f'{REL_URLS["requests"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    inst = await request_des.for_detail(resp)
    if keyboard_key == 'request_detail':
        keyboard = await keyboard_cor(pk=pk, page=callback_data.get('page'),
                                      key=callback_data.get('key'))
    else:
        keyboard = await keyboard_cor(pk=pk, page=callback_data.get('page'),
                                      key=callback_data.get('key'))
    await call.message.answer(inst.data, reply_markup=keyboard)
    await call.answer()


@dp.message_handler(Text(equals=['Входящие запросы на добавление в шахматку', 'Income request to chest']))
async def requests_to_chest(message: types.Message):
    await handle_list(message, key='requests', page='1', deserializer=request_des,
                      keyboard=get_keyboard_for_list, detail_action='request_detail',
                      list_action='request_list')


@dp.callback_query_handler(LIST_CB.filter(action='request_list'))
async def request_to_chest_list(call: types.CallbackQuery, callback_data: dict):
    page = callback_data.get('page')
    key = callback_data.get('key')
    await handle_list(call, key=key, page=page, deserializer=request_des,
                      keyboard=get_keyboard_for_list, detail_action='request_detail',
                      list_action='request_list')


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='request_detail'))
async def request_detail(call: types.CallbackQuery, callback_data: dict):
    await get_request(call, callback_data, 'request_detail')
