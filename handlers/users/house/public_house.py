import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher
from keyboards.inline.user_keyboards import get_keyboard_for_list, get_keyboard_for_house
from keyboards.callbacks.user_callback import LIST_CB, DETAIL_WITH_PAGE_CB

from deserializers.house import HouseDeserializer

from middlewares import _

from handlers.users.utils import handle_list, send_with_image

from utils.session.url_dispatcher import REL_URLS


house_des = HouseDeserializer()


keyboard_house_detail = {
    'house_detail': get_keyboard_for_house
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
                                      action='house_list_new' if resp.get('image') else 'house_list')
    if resp.get('image'):
        await send_with_image(call, resp, pk, inst.data, keyboard,
                              'image')
    else:
        await call.message.answer(inst.data, reply_markup=keyboard)
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
