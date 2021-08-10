import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher
from keyboards.inline.user_keyboards import (get_keyboard_for_list, get_keyboard_for_house, get_keyboard_for_my_house,
                                             get_keyboard_for_flat, get_keyboard_for_flat_list, get_keyboard_for_booked_flat,
                                             get_keyboard_for_flat_detail_house, get_keyboard_for_my_flat)
from keyboards.inline import create_house
from keyboards.callbacks.user_callback import LIST_CB, DETAIL_WITH_PAGE_CB, DETAIL_CB, LIST_CB_WITH_PK

from deserializers.house import HouseDeserializer, FlatDeserializer

from middlewares import _

from handlers.users.utils import handle_list, send_with_image

from utils.session.url_dispatcher import REL_URLS
from utils.db_api.models import User


house_des = HouseDeserializer()
flat_des = FlatDeserializer()


keyboard_house_detail = {
    'house_detail': get_keyboard_for_house,
    'my_house_detail': get_keyboard_for_my_house,
    'from_flat_house_detail': get_keyboard_for_flat_detail_house
}
keyboard_flat_detail = {
    'flat_detail': get_keyboard_for_flat,
    'my_flat_detail': get_keyboard_for_my_flat,
    'booked_flat': get_keyboard_for_booked_flat
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
    elif keyboard_key == 'from_flat_house_detail':
        keyboard = await keyboard_cor(page=callback_data.get('page'),
                                      key=callback_data.get('key'),
                                      action='my_flats_list')
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
    if keyboard_key == 'booked_flat':
        action = 'my_flats_list'
    else:
        action = 'flats_list'
    keyboard = await keyboard_cor(key=callback_data.get('key'),
                                  page=callback_data.get('page'),
                                  action=action,
                                  pk=pk,
                                  house_pk=resp.get('house_pk'))
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


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='from_flat_house_detail'))
async def house_detail(call: types.CallbackQuery, callback_data: dict):
    await get_house(call, callback_data, 'from_flat_house_detail')


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
    pk = callback_data.get('pk')
    url = f'{REL_URLS["flats"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    user = await User.get(user_id=call.from_user.id)
    if resp.get('sales_department_pk') == user.swipe_id:
        key = 'my_flat_detail'
    else:
        key = 'flat_detail'
    await get_flat(call, callback_data, key)


@dp.callback_query_handler(DETAIL_CB.filter(action='booking_flat'))
async def booking_flat(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = REL_URLS['booking_flat'].format(flat_pk=pk)
    data = {'booking': '1'}
    resp = await Conn.patch(url, data=data, user_id=call.from_user.id)
    if resp.get('Error'):
        await call.message.answer(_('Произошла ошибка'))
        await call.answer(resp.get('Error'), show_alert=True)
    else:
        await call.answer(_('Квартира забронирована. Запрос на добавление в шахматку отправлен администратору дома'),
                          show_alert=True)


@dp.message_handler(Text(equals=['Мои квартиры', 'My flats']))
async def my_flats(message: types.Message):
    await message.answer(_('Список забронированных квартир'))
    user = await User.get(user_id=message.from_user.id)
    url = f'{REL_URLS["flats_public"]}?client_pk={user.swipe_id}&page=1'
    await handle_list(message, key='flats', page='1',
                      keyboard=get_keyboard_for_flat_list,
                      detail_action='my_flat_detail', list_action='my_flats_list',
                      deserializer=flat_des, pk=0, custom_url=url)


@dp.callback_query_handler(LIST_CB_WITH_PK.filter(action='my_flats_list'))
async def my_flats_callback(call: types.CallbackQuery, callback_data: dict):
    key = callback_data.get('key')
    page = callback_data.get('page')
    user = await User.get(user_id=call.from_user.id)
    url = f'{REL_URLS["flats_public"]}?client_pk={user.swipe_id}&page={page}'
    await handle_list(call, key=key, page=page,
                      keyboard=get_keyboard_for_flat_list,
                      detail_action='my_flat_detail', list_action='my_flats_list',
                      deserializer=flat_des, pk=0, custom_url=url, new_callback_answer=True)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='my_flat_detail'))
async def my_flat_detail(call: types.CallbackQuery, callback_data: dict):
    await get_flat(call, callback_data, keyboard_key='booked_flat')


@dp.callback_query_handler(DETAIL_CB.filter(action='unbooking_flat'))
async def unbooking_flat(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = REL_URLS['booking_flat'].format(flat_pk=pk)
    data = {'booking': '0'}
    resp = await Conn.patch(url, data=data, user_id=call.from_user.id)
    if resp.get('Error'):
        await call.message.answer(_('Произошла ошибка'))
        await call.answer(resp.get('Error'), show_alert=True)
    else:
        await call.answer(_('Бронь снята'), show_alert=True)
        user = await User.get(user_id=call.from_user.id)
        url = f'{REL_URLS["flats_public"]}?client_pk={user.swipe_id}&page=1'
        await handle_list(call, key='flats', page='1',
                          keyboard=get_keyboard_for_flat_list ,
                          detail_action='my_flat_detail', list_action='my_flats_list',
                          deserializer=flat_des, pk=0, custom_url=url, new_callback_answer=True)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='add_building'))
async def add_building(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    resp, status = await Conn.post(REL_URLS['buildings'], data={'house': pk}, user_id=call.from_user.id)
    if status == 201:
        await call.answer(_('Корпус добавлен'), show_alert=True)
        await get_house(call, callback_data, 'my_house_detail')
    else:
        await call.answer(_('Произошла ошибка'))
        for key, value in resp.items():
            logging.info(f'{key}: {value}\n')


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='add_section'))
async def add_section(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    page = callback_data.get('page')
    key = callback_data.get('key')
    resp = await Conn.get(REL_URLS['buildings'], params={'house': pk}, user_id=call.from_user.id)
    buildings = resp.get('results')
    if buildings:
        keyboard = await create_house.get_building_keyboard(items=resp.get('results'), action='add_section_building',
                                                            page=page, key=key)
        text = ''
        for index, item in enumerate(buildings, start=1):
            text += f'{index}. {item["full_name"]}\n'
        await call.message.answer(text, reply_markup=keyboard)
        await call.answer()
    else:
        await call.answer(_('Нет корпусов. Сперва добавьте их'), show_alert=True)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='add_section_building'))
async def save_section(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    resp, status = await Conn.post(REL_URLS['sections'], data={'building': pk}, user_id=call.from_user.id)
    if status == 201:
        callback_data['pk'] = resp['house']
        await call.answer(_('Секция добавлена'), show_alert=True)
        await get_house(call, callback_data, 'my_house_detail')
    else:
        await call.answer(_('Произошла ошибка'))
        for key, value in resp.items():
            logging.info(f'{key}: {value}\n')


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='add_floor'))
async def add_floor(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    page = callback_data.get('page')
    key = callback_data.get('key')
    resp = await Conn.get(REL_URLS['sections'], params={'house': pk}, user_id=call.from_user.id)
    sections = resp.get('results')
    if sections:
        keyboard = await create_house.get_building_keyboard(items=resp.get('results'), action='add_floor_section',
                                                            page=page, key=key)
        text = ''
        for index, item in enumerate(sections, start=1):
            text += f'{index}. {item["full_name"]}\n'
        await call.message.answer(text, reply_markup=keyboard)
        await call.answer()
    else:
        await call.answer(_('Нет секций. Добавьте их сперва'), show_alert=True)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='add_floor_section'))
async def save_floor(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    resp, status = await Conn.post(REL_URLS['floors'], data={'section': pk}, user_id=call.from_user.id)
    if status == 201:
        callback_data['pk'] = resp['house']
        await call.answer(_('Этаж добавлен'), show_alert=True)
        await get_house(call, callback_data, 'my_house_detail')
    else:
        await call.answer(_('Произошла ошибка'))
        for key, value in resp.items():
            logging.info(f'{key}: {value}\n')


@dp.callback_query_handler(DETAIL_CB.filter(action='delete_flat'))
async def delete_flat(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["flats"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    resp_delete, status = await Conn.delete(url, user_id=call.from_user.id)
    if status == 204:
        await call.answer()
        data = {'pk': resp.get('house_pk'),
                'page': '1',
                'key': 'houses'}
        await get_house(call, data, 'my_house_detail')
    else:
        await call.answer(_('Произошла ошибка. Попробуйте ещё раз'))


@dp.callback_query_handler(LIST_CB_WITH_PK.filter(action='house_structure_list'))
async def house_structure_list(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    key = callback_data.get('key')
    resp = await Conn.get(REL_URLS[key], params={'house': pk}, user_id=call.from_user.id)
    objects = resp.get('results')
    if objects:
        keyboard = await create_house.get_building_keyboard(items=objects,
                                                            page=callback_data.get('page'),
                                                            key=key,
                                                            action='delete_house_structure')
        text = ''
        for index, item in enumerate(objects, start=1):
            text += f'{index}. {item["full_name"]}\n'
            text += f'Есть связанные объекты\n' if item.get('has_related') is True else 'Пусто\n'
        await call.message.answer(text, reply_markup=keyboard)
        await call.answer()
    else:
        await call.answer(_('Ничего нет'), show_alert=True)


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='delete_house_structure'))
async def delete_house_structure(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    key = callback_data.get('key')
    url = f'{REL_URLS[key]}{pk}/'
    resp_detail = await Conn.get(url, user_id=call.from_user.id)
    resp, status = await Conn.delete(url, user_id=call.from_user.id)
    if status == 204:
        await call.answer(_('Объект удален'))
        callback_data['pk'] = resp_detail.get('house')
        callback_data['key'] = 'houses'
        await get_house(call, callback_data, 'my_house_detail')
    else:
        await call.answer(_('Произошла ошибка: ' + status))


@dp.callback_query_handler(LIST_CB_WITH_PK.filter(action='news_list'))
async def news_list(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    resp = await Conn.get(REL_URLS['news'], params={'house': pk}, user_id=call.from_user.id)
    objects = resp.get('results')
    if objects:
        keyboard = await create_house.get_building_keyboard('delete_news', objects,
                                                            'news', '1')
        text = ''
        for index, item in enumerate(objects, start=1):
            text += f'{index}. {item["title"]}'
        await call.message.answer(text, reply_markup=keyboard)
    else:
        await call.answer(_('Новостей нет'))


@dp.callback_query_handler(DETAIL_WITH_PAGE_CB.filter(action='delete_news'))
async def delete_news(call: types.CallbackQuery, callback_data: dict):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["news"]}{pk}/'
    resp_detail = await Conn.get(url, user_id=call.from_user.id)
    resp, status = await Conn.delete(url, user_id=call.from_user.id)
    if status == 204:
        await call.answer(_('Удалено'))
        callback_data['pk'] = resp_detail.get('house')
        callback_data['key'] = 'houses'
        await get_house(call, callback_data, 'my_house_detail')
    else:
        await call.answer(_('Ошибка'))
        for key, value in resp.items():
            logging.info(f'{key} - {value}')
