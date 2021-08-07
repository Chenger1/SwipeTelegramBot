import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher
from keyboards.inline.user_keyboards import (get_keyboard_for_list, get_keyboard_for_house, get_keyboard_for_my_house,
                                             get_keyboard_for_flat, get_keyboard_for_flat_list)
from keyboards.callbacks.user_callback import LIST_CB, DETAIL_WITH_PAGE_CB, DETAIL_CB, LIST_CB_WITH_PK

from deserializers.house import HouseDeserializer, FlatDeserializer

from middlewares import _

from handlers.users.utils import handle_list, send_with_image

from utils.session.url_dispatcher import REL_URLS


house_des = HouseDeserializer()
flat_des = FlatDeserializer()


keyboard_house_detail = {
    'house_detail': get_keyboard_for_house,
    'my_house_detail': get_keyboard_for_my_house
}
keyboard_flat_detail = {
    'flat_detail': get_keyboard_for_flat,
    'my_flat_detail': None
}


async def get_house(call: types.CallbackQuery, callback_data: dict,
                    keyboard_key: str):
    keyboard_cor = keyboard_house_detail[keyboard_key]
    logging.info(callback_data)
    pk = callback_data.get('pk')
    url = f'{REL_URLS["houses_public"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    inst = await house_des.for_detail(resp)
    if keyboard_key == 'house_detail':
        keyboard = await keyboard_cor(page=callback_data.get('page'),
                                      key=callback_data.get('key'),
                                      action='house_list_new' if resp.get('image') else 'house_list',
                                      pk=pk)
    else:
        keyboard = await keyboard_cor(page=callback_data.get('page'),
                                      key=callback_data.get('key'),
                                      action='my_house_list_new' if resp.get('image') else 'my_house_list',
                                      pk=pk)
    if resp.get('image'):
        await send_with_image(call, resp, pk, inst.data, keyboard,
                              'image')
    else:
        await call.message.answer(inst.data, reply_markup=keyboard)
    await call.answer()


async def get_flat(call: types.CallbackQuery, callback_data: dict,
                   keyboard_key: str):
    keyboard_cor = keyboard_flat_detail[keyboard_key]
    logging.info(callback_data)
    pk = callback_data.get('pk')
    url = f'{REL_URLS["flats_public"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    inst = await flat_des.for_detail(resp)
    if keyboard_key == 'flat_detail':
        keyboard = await keyboard_cor(key=callback_data.get('key'),
                                      page=callback_data.get('page'),
                                      action='flats_list',
                                      pk=pk,
                                      house_pk=resp.get('house_pk'))
    else:
        keyboard = None
    await send_with_image(call, resp, pk, inst.data, keyboard, 'schema')
    await call.answer()


@dp.message_handler(Text(equals=['Список домов', 'Houses list']))
async def get_house_keyboard(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_HOUSES', message.from_user.id)
    logging.info(path)
    await message.answer(_('Меню домов'), reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Все дома', 'All houses']))
async def house_list(message: types.Message, state: FSMContext):
    params = await state.get_data()
    await message.answer(_('Список всех домов'))
    await handle_list(message, key='houses_public', page='1', deserializer=house_des,
                      keyboard=get_keyboard_for_list, detail_action='house_detail',
                      list_action='house_list', params=params)


@dp.callback_query_handler(LIST_CB.filter(action='house_list'))
async def house_list(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_list(call, key=key, page=page, deserializer=house_des,
                      keyboard=get_keyboard_for_list, detail_action='house_detail',
                      list_action='house_list', params=params)


@dp.callback_query_handler(LIST_CB.filter(action='house_list_new'))
async def house_list_new(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_list(call, key=key, page=page, params=params, keyboard=get_keyboard_for_list,
                      detail_action='house_detail', list_action='house_list',
                      deserializer=house_des, new_callback_answer=True)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='house_detail'))
async def house_detail(call: types.CallbackQuery, callback_data: dict):
    await get_house(call, callback_data, 'house_detail')


@dp.message_handler(Text(equals=['Мои дома', 'My houses']))
async def my_houses(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_3_MY_HOUSES', message.from_user.id)
    params = await state.get_data()
    await message.answer(_('Мои дома'), reply_markup=keyboard)
    await handle_list(message, key='houses', page='1', params=params, keyboard=get_keyboard_for_list,
                      detail_action='my_house_detail', list_action='my_house_list',
                      deserializer=house_des)
    await state.update_data(path=path)


@dp.callback_query_handler(LIST_CB.filter(action='my_house_list'))
async def my_house_list(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_list(call, key=key, page=page, deserializer=house_des,
                      detail_action='my_house_detail', list_action='my_house_list',
                      keyboard=get_keyboard_for_list, params=params)


@dp.callback_query_handler(LIST_CB.filter(action='my_house_list_new'))
async def my_house_list(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data.get('page')
    key = callback_data.get('key')
    params = await state.get_data()
    await handle_list(call, key=key, page=page, deserializer=house_des,
                      detail_action='my_house_detail', list_action='my_house_list',
                      keyboard=get_keyboard_for_list, params=params,
                      new_callback_answer=True)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='my_house_detail'))
async def my_house_detail(call: types.CallbackQuery, callback_data: dict):
    await get_house(call, callback_data, 'my_house_detail')


@dp.callback_query_handler(DETAIL_CB.filter(action='delete_house'))
async def delete_house(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    pk = callback_data.get('pk')
    key = callback_data.get('key')
    page = callback_data.get('page')
    params = await state.get_data()
    url = f'{REL_URLS["houses"]}{pk}/'
    resp, status = await Conn.delete(url, user_id=call.from_user.id)
    if status == 204:
        await handle_list(call, key=key, page=page, deserializer=house_des,
                          detail_action='my_house_detail', list_action='my_house_list',
                          keyboard=get_keyboard_for_list, params=params,
                          new_callback_answer=True)
        await call.answer(_('Дом был удален'))
    else:
        await call.answer(_('Произошла ошибка'))


@dp.callback_query_handler(LIST_CB_WITH_PK.filter(action='flats_list'))
async def house_flats(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    key = callback_data.get('key')
    page = callback_data.get('page')
    params = callback_data.get('params')
    url = f'{REL_URLS["flats_public"]}?house__pk={pk}&page={page}'
    await handle_list(call, key=key, page=page, params=params,
                      keyboard=get_keyboard_for_flat_list, detail_action='flat_detail',
                      list_action='flats_list_edit', deserializer=flat_des,
                      new_callback_answer=True, custom_url=url, pk=pk)


@dp.callback_query_handler(LIST_CB_WITH_PK.filter(action='flats_list_edit'))
async def house_flats(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    key = callback_data.get('key')
    page = callback_data.get('page')
    params = callback_data.get('params')
    url = f'{REL_URLS["flats_public"]}?house__pk={pk}&page={page}'
    await handle_list(call, key=key, page=page, params=params,
                      keyboard=get_keyboard_for_flat_list, detail_action='flat_detail',
                      list_action='flats_list_edit', deserializer=flat_des,
                      custom_url=url, pk=pk)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='flat_detail'))
async def flat_detail(call: types.CallbackQuery, callback_data: dict):
    await get_flat(call, callback_data, 'flat_detail')
