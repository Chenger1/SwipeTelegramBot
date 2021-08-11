from aiogram import types
from aiogram.dispatcher.filters.builtin import Text

from keyboards.inline.user_keyboards import get_keyboard_for_list
from loader import dp, Conn, log
from utils.db_api.models import User

from utils.session.url_dispatcher import REL_URLS

from handlers.users.utils import handle_list

from deserializers.house import RequestDeserializer

from keyboards.callbacks.user_callback import DETAIL_WITH_PAGE_CB, LIST_CB
from keyboards.inline.user_keyboards import get_keyboard_for_request_detail

from middlewares import _

request_des = RequestDeserializer()

keyboard_request_detail = {
    'request_detail': get_keyboard_for_request_detail
}


async def get_request(call: types.CallbackQuery, callback_data: dict, keyboard_key: str):
    keyboard_cor = keyboard_request_detail[keyboard_key]
    log.debug(callback_data)
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


async def send_request_answer(call: types.CallbackQuery, data: dict, pk: int):
    url = f'{REL_URLS["requests"]}{pk}/'
    resp = await Conn.patch(url, data=data, user_id=call.from_user.id)
    if not resp.get('id'):
        await call.answer(_('Произошла ошибка'))
        return
    resp_detail = await Conn.get(url, user_id=call.from_user.id)
    return resp_detail


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


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='approve_request'))
async def approve_request(call: types.CallbackQuery, callback_data: dict):
    data = {'approved': True}
    pk = callback_data.get('pk')
    url = f'{REL_URLS["requests"]}{pk}/'
    resp = await Conn.patch(url, data=data, user_id=call.from_user.id)
    if not resp.get('id'):
        await call.answer(_('Произошла ошибка'))
        return
    resp_detail = await Conn.get(url, user_id=call.from_user.id)
    client = await User.get_or_none(swipe_id=resp_detail['flat_display']['client_pk'])
    if client:
        text = _('<b>*Системное сообщение*</b>\n' +
                 'Ваш запрос на квартиру №{flat} в {house} <b>Одобрен</b>\n').format(
            flat=resp['flat_display']['number'],
            house=resp['flat_display']['house'])
        await call.bot.send_message(chat_id=client.user_id, text=text)
    await call.answer(_('Одобрено'))
    key = callback_data.get('key')
    page = callback_data.get('page')
    await handle_list(call, key=key, page=page, deserializer=request_des,
                      keyboard=get_keyboard_for_list, detail_action='request_detail',
                      list_action='request_list')


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='disapprove_request'))
async def approve_request(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["requests"]}{pk}/'
    resp_detail = await Conn.get(url, user_id=call.from_user.id)
    client_pk = resp_detail['flat_display']['client_pk']

    resp, status = await Conn.delete(url, user_id=call.from_user.id)
    if status == 204:
        client = await User.get_or_none(swipe_id=client_pk)
        if client:
            text = _('<b>*Системное сообщение*</b>\n' +
                     'Ваш запрос на квартиру №{flat} в {house} <b>Одобрен</b>\n' +
                     'Бронь квартиры отменена').format(flat=resp_detail['flat_display']['number'],
                                                       house=resp_detail['flat_display']['house'])
            await call.bot.send_message(chat_id=client.user_id, text=text)
        await call.answer(_('Отказано'))
        key = callback_data.get('key')
        page = callback_data.get('page')
        await handle_list(call, key=key, page=page, deserializer=request_des,
                          keyboard=get_keyboard_for_list, detail_action='request_detail',
                          list_action='request_list')
    else:
        await call.answer(_('Произошла ошибка'))
