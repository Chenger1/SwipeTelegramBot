import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher
from keyboards.inline.user_keyboards import (get_keyboard_for_list, get_keyboard_for_notary_list,
                                             get_keyboard_for_complaint_list)
from keyboards.callbacks.user_callback import LIST_CB, DETAIL_WITH_PAGE_CB
from deserializers.user import UserDeserializer
from deserializers.post import ComplaintDeserializer

from middlewares import _
from utils.db_api.models import User

from utils.session.url_dispatcher import REL_URLS
from handlers.users.utils import handle_list

user_des = UserDeserializer()
complaint_des = ComplaintDeserializer()


@dp.message_handler(Text(equals=['Панель администратора', 'Admin Panel']), is_admin=True)
async def admin_panel(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_ADMIN_PANEL', message.from_user.id)
    await message.answer(_('Панель администратора'), reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Список нотариусов', 'Notary List']), is_admin=True)
async def notary_list(message: types.Message):
    await handle_list(message, page='1', key='users', params={'role': 'NOTARY'},
                      deserializer=user_des, detail_action='user_notary_detail',
                      list_action='user_notary_list', keyboard=get_keyboard_for_list)


@dp.callback_query_handler(LIST_CB.filter(action='user_notary_list'), is_admin=True)
async def notary_list_callback(call: types.CallbackQuery, callback_data: dict):
    page = callback_data.get('page')
    key = callback_data.get('key')
    await handle_list(call, page=page, key=key, params={'role': 'NOTARY'},
                      deserializer=user_des, detail_action='user_notary_detail',
                      list_action='user_notary_list', keyboard=get_keyboard_for_list)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='user_notary_detail'))
async def notary_detail(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["users"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    if resp.get('pk'):
        keyboard = await get_keyboard_for_notary_list(pk, callback_data.get('page'), callback_data.get('key'))
        inst = await user_des.for_detail(resp)
        await call.answer()
        await call.message.answer(inst.data, reply_markup=keyboard)
    else:
        await call.answer(_('Произошла ошибка'))


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='remove_from_notary'))
async def remove_from_notary(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["users"]}{pk}/'
    resp = await Conn.patch(url, data={'role': 'USER'}, user_id=call.from_user.id)
    if resp.get('pk'):
        await call.answer(_('Пользователь убран из списка нотариусов'))
        page = callback_data.get('page')
        key = callback_data.get('key')
        await handle_list(call, page=page, key=key, params={'role': 'NOTARY'},
                          deserializer=user_des, detail_action='user_notary_detail',
                          list_action='user_notary_list', keyboard=get_keyboard_for_list)
    else:
        await call.answer(_('Произошла ошибка'))
        for key, value in resp.items():
            logging.info(f'{key} - {value}')


@dp.message_handler(Text(equals=['Жалобы', 'Complaints']), is_admin=True)
async def complaints_list(message: types.Message):
    await handle_list(message, page='1', key='complaint_admin', deserializer=complaint_des,
                      detail_action='complaint_detail', list_action='complaint_list',
                      keyboard=get_keyboard_for_list)


@dp.callback_query_handler(LIST_CB.filter(action='complaint_list'))
async def complaints_list_callback(call: types.CallbackQuery, callback_data: dict):
    page = callback_data.get('page')
    key = callback_data.get('key')
    await handle_list(call, page=page, key=key, deserializer=complaint_des,
                      detail_action='complaint_detail', list_action='complaint_list',
                      keyboard=get_keyboard_for_list)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='complaint_detail'))
async def complaint_detail(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["complaint_admin"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    if resp.get('id'):
        keyboard = await get_keyboard_for_complaint_list(pk=pk, page=callback_data.get('page'),
                                                         key=callback_data.get('key'))
        inst = await complaint_des.for_detail(resp)
        await call.answer()
        await call.message.edit_text(inst.data, reply_markup=keyboard)
    else:
        await call.answer(_('Произошла ошибка'))


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='approve_complaint'), is_admin=True)
async def approve_complaint(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["complaint_admin"]}{pk}/'
    resp_detail = await Conn.get(url, user_id=call.from_user.id)
    rejected_type = resp_detail.get('type')
    post_pk = resp_detail.get('post')
    url_post = f'{REL_URLS["posts"]}{post_pk}/'
    data = {
        'rejected': True,
        'reject_message': rejected_type
    }
    resp_reject = await Conn.patch(url_post, data=data, params={'for_user': resp_detail['post_author']},
                                   user_id=call.from_user.id)
    if resp_reject.get('id'):
        user = await User.get_or_none(user_id=resp_reject.get('user'))
        await call.answer(_('Объявление заблокировано'))
        if user:
            flat = f'{resp_reject["flat_info"]["floor"]} №{resp_reject["flat_info"]["number"]}'
            text = _('<b>** Системное сообщение **</b>' +
                     'Ваша публикации для квартиры {flat} в доме {house}' +
                     'была заблокирована по причине {message}').format(flat=flat,
                                                                       house=resp_reject['flat_info']['house'],
                                                                       message=resp_reject['reject_message_display'])
            await call.bot.send_message(chat_id=user.user_id, text=text)
    else:
        await call.answer(_('Произошла ошибка'))
        for key, value in resp_reject.items():
            logging.info(f'{key} - {value}')


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='disapprove_complaint'), is_admin=True)
async def disapprove_complaint(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["complaint_admin"]}{pk}/'
    resp_detail = await Conn.get(url, user_id=call.from_user.id)
    post_pk = resp_detail.get('post')
    url_post_detail = f'{REL_URLS["posts"]}{post_pk}/'
    data = {
        'rejected': False,
        'reject_message': ''
    }
    resp_post_detail = await Conn.patch(url_post_detail, data=data, params={'for_user': resp_detail['post_author']},
                                        user_id=call.from_user.id)
    if resp_post_detail.get('id'):

        resp, status = await Conn.delete(url, user_id=call.from_user.id)
        if status == 204:

            user = await User.get_or_none(user_id=resp_detail['user'])
            if user:
                flat = f'{resp_post_detail["flat_info"]["floor"]} №{resp_post_detail["flat_info"]["number"]}'
                text = _('<b>** Системное сообщение **</b>' +
                         'Ваша жалоба на объявление для квартиры {flat} в доме {house}' +
                         'была отвергнута').format(flat=flat,
                                                   house=resp_post_detail['flat_info']['house'])
                await call.bot.send_message(chat_id=user.user_id, text=text)
            await call.answer(_('В жалобе отказано'))
            await handle_list(call, page='1', key='complaint_admin', deserializer=complaint_des,
                              detail_action='complaint_detail', list_action='complaint_list',
                              keyboard=get_keyboard_for_list)
        else:
            await call.answer(_('Произошла ошибка'))
            for key, value in resp.items():
                logging.info(f'{key} - {value}')
    else:
        await call.answer(_('Произошла ошибка'))
        for key, value in resp_post_detail.items():
            logging.info(f'{key} - {value}')
