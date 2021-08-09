import logging
import os

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from keyboards.callbacks.user_callback import DETAIL_CB
from loader import dp, Conn

from deserializers.house import HouseDeserializer

from states.state_groups import CreateHouse

from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline import create_house

from middlewares import _

from utils.db_api.models import File
from utils.session.url_dispatcher import REL_URLS

from handlers.users.utils import update_state


house_des = HouseDeserializer()


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreateHouse)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    keys_to_delete = ('create_house', 'house_info')
    new_dict = {}
    for key, value in data.items():
        if key not in keys_to_delete:
            new_dict[key] = value
    await state.finish()
    new_dict['path'] = path
    await state.update_data(**new_dict)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=CreateHouse)
async def save_house(message: types.Message, state: FSMContext):
    data = await state.get_data()
    house_data = data.get('create_house')
    keys = ('name', 'address', 'city', 'tech', 'territory', 'payment_options',
            'description')
    if all(key in house_data for key in keys):
        await message.answer(_('Подтверждаете?'),
                             reply_markup=create_house.confirm_keyboard)
        await CreateHouse.SAVE.set()
    else:
        text = _('Вы не указали: \n')
        if not house_data.get('name'):
            text += _('Название\n')
        if not house_data.get('address'):
            text += _('Адрес\n')
        if not house_data.get('city'):
            text += _('Город\n')
        if not house_data.get('tech'):
            text += _('Технологию строительства\n')
        if not house_data.get('territory'):
            text += _('Тип территории\n')
        if not house_data.get('payment_options'):
            text += _('Предпочитаемый способ оплаты\n')
        if not house_data.get('description'):
            text += _('Описание\n')
        await message.answer(text)


@dp.message_handler(Text(equals=['Перейти к названию', 'Go to name']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Введите название дома'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['name']))
    await CreateHouse.NAME.set()


@dp.message_handler(Text(equals=['Перейти к городу', 'Go to city']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Введите город'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['city']))
    await CreateHouse.CITY.set()


@dp.message_handler(Text(equals=['Перейти к адресу', 'Go to address']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Введите адрес дома'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['address']))
    await CreateHouse.ADDRESS.set()


@dp.message_handler(Text(equals=['Перейти к технологии строительства', 'Go to technology']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите технологию строительства'), reply_markup=create_house.tech_keyboard)
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['tech_display']))
    await CreateHouse.TECH.set()


@dp.message_handler(Text(equals=['Перейти к территории', 'Go to territory']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите тип территории'), reply_markup=create_house.terr_keyboard)
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['territory_display']))
    await CreateHouse.TERR.set()


@dp.message_handler(Text(equals=['Перейти к платежным способам', 'Go to payment methods']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите предпочитаемые способы платежа'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['payment_options_display']))
    await CreateHouse.PAYMENT_OPTIONS.set()


@dp.message_handler(Text(equals=['Перейти к описанию', 'Go to description']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Добавьте описание'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['description']))
    await CreateHouse.DESCRIPTION.set()


@dp.message_handler(Text(equals=['Перейти к статусу', 'Go to status']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите статус дома'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['status_display']))
    await CreateHouse.ROLE.set()


@dp.message_handler(Text(equals=['Перейти к типу', 'Go to type']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Введите тип дома'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['type_display']))
    await CreateHouse.TYPE.set()


@dp.message_handler(Text(equals=['Перейти к классу дома', 'Go to house class']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите класс дома дома'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['house_class_display']))
    await CreateHouse.HOUSE_CLASS.set()


@dp.message_handler(Text(equals=['Перейти к расстоянию до моря', 'Go to distance to sea']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Введите расстояние до моря'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['distance_to_sea']))
    await CreateHouse.SEA.set()


@dp.message_handler(Text(equals=['Перейти к высоте потолков', 'Go to ceiling height']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Введите высоту потолков'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['ceiling_height']))
    await CreateHouse.HEIGHT.set()


@dp.message_handler(Text(equals=['Перейти к газопроводу', 'Go to gas']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите тип газопровода'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['gas_display']))
    await CreateHouse.GAS.set()


@dp.message_handler(Text(equals=['Перейти к отоплению', 'Go to heating']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите тип отопления'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['heating_display']))
    await CreateHouse.HEATING.set()


@dp.message_handler(Text(equals=['Перейти к электричеству', 'Go to electricity']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите тип электроподачи'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['electricity_display']))
    await CreateHouse.ELECTRICITY.set()


@dp.message_handler(Text(equals=['Перейти к канализации', 'Go to sewerage']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите тип канализации'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['sewerage_display']))
    await CreateHouse.SEWERAGE.set()


@dp.message_handler(Text(equals=['Перейти к водоснабжению', 'Go to water supply']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Выберите тип водоснабжения'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['water_supply_display']))
    await CreateHouse.WATER.set()


@dp.message_handler(Text(equals=['Перейти к спортивной площадке', 'Go to house class']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Есть ли в вашем доме(или рядом с ним) спортивная площадка?'),
                         reply_markup=await create_house.get_advantages_keyboard('add_playground'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        text = _('Есть') if state_data['create_house']['playground'] else _('Нет')
        await message.answer(text)
    await CreateHouse.PLAYGROUND.set()


@dp.message_handler(Text(equals=['Перейти к парковке', 'Go to car park']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Есть ли в вашем доме(или рядом с ним) парковка?'),
                         reply_markup=await create_house.get_advantages_keyboard('add_car_park'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        text = _('Есть') if state_data['create_house']['car_park'] else _('Нет')
        await message.answer(text)
    await CreateHouse.CAR_PARK.set()


@dp.message_handler(Text(equals=['Перейти к магазину', 'Go to shop']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Есть ли в вашем доме(или рядом с ним) магазин?'),
                         reply_markup=await create_house.get_advantages_keyboard('add_shop'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        text = _('Есть') if state_data['create_house']['shop'] else _('Нет')
        await message.answer(text)
    await CreateHouse.SHOP.set()


@dp.message_handler(Text(equals=['Перейти к детской площадке', 'Go to child playground']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Есть ли в вашем доме(или рядом с ним) детская площадка?'),
                         reply_markup=await create_house.get_advantages_keyboard('add_child_playground'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        text = _('Есть') if state_data['create_house']['child_playground'] else _('Нет')
        await message.answer(text)
    await CreateHouse.CHILD_PLAYGROUND.set()


@dp.message_handler(Text(equals=['Перейти к лифту', 'Go to elevator']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Есть ли в вашем доме лифт?'),
                         reply_markup=await create_house.get_advantages_keyboard('add_elevator'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        text = _('Есть') if state_data['create_house']['elevator'] else _('Нет')
        await message.answer(text)
    await CreateHouse.ELEVATOR.set()


@dp.message_handler(Text(equals=['Перейти к охране', 'Go to security']), state=CreateHouse)
async def go_to_house_name(message: types.Message, state: FSMContext):
    await message.answer(_('Есть ли в вашем доме охрана?'),
                         reply_markup=await create_house.get_advantages_keyboard('add_security'))
    state_data = await state.get_data()
    if state_data.get('house_info'):
        text = _('Есть') if state_data['create_house']['security'] else _('Нет')
        await message.answer(text)
    await CreateHouse.SECURITY.set()


@dp.message_handler(Text(equals=['Перейти к картинке', 'Go to image']), state=CreateHouse)
async def go_to_house_name(message: types.Message):
    await message.answer(_('Добавьте изображение'))
    await CreateHouse.IMAGE.set()


@dp.callback_query_handler(DETAIL_CB.filter(action='edit_house'))
async def edit_house(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["houses_public"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    image_name = resp.get('image').split('/')[-1]
    file = await File.get(filename=image_name)
    house_data = {
        'name': resp['name'],
        'city': resp['city'],
        'address': resp['address'],
        'sea': str(resp['distance_to_sea']),
        'height': str(resp['ceiling_height']),
        'playground': str(resp['playground']),
        'car_park': str(resp['car_park']),
        'shop': str(resp['shop']),
        'child_playground': str(resp['child_playground']),
        'high_speed_elevator': str(resp['high_speed_elevator']),
        'security': str(resp['security']),
        'tech': resp['tech'],
        'territory': resp['territory'],
        'payment_options': resp['payment_options'],
        'description': resp['description'],
        'role': resp['role'],
        'type': resp['type'],
        'house_class': resp['house_class'],
        'gas': resp['gas'],
        'heating': resp['heating'],
        'electricity': resp['electricity'],
        'sewerage': resp['sewerage'],
        'water': resp['water_supply'],
        'image': file.file_id
    }
    if image_name not in os.listdir('photos/'):
        file = await call.bot.get_file(file.file_id)
        await file.download()
    inst = await house_des.for_detail(resp)
    keyboard, path = await dispatcher('LEVEL_4_ADD_HOUSE', call.from_user.id)
    text = _('Сейчас: \n' + inst.data)
    if resp.get('image'):
        await call.bot.send_photo(photo=file.file_id, caption=text,
                                  chat_id=call.from_user.id)
    else:
        await call.message.answer(text)
    await call.message.answer(_('Редактируйте информацию\n' +
                                'Введите новое название дома\n' +
                                'Сейчас: {name}').format(name=resp['name']), reply_markup=keyboard)
    logging.info({'path': path})
    await CreateHouse.NAME.set()
    await state.update_data(path=path, house_info=resp, create_house=house_data)
    await call.answer()


@dp.message_handler(Text(equals=['Добавить дом', 'Add house']))
async def add_house(message: types.Message, state: FSMContext):
    await CreateHouse.STARTER.set()
    keyboard, path = await dispatcher('LEVEL_4_ADD_HOUSE', message.from_user.id)
    await message.answer(_('Введите название дома'), reply_markup=keyboard)
    await state.update_data(path=path)
    await CreateHouse.NAME.set()
    await state.update_data(create_house={})


@dp.message_handler(state=CreateHouse.NAME)
async def house_name(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    answer = message.text
    await update_state(state, answer, 'name', 'create_house')
    if state_data.get('house_info'):
        await message.answer(_('Текущий город: {city}').format(city=state_data['create_house']['name']))
    await message.answer(_('Введите город'))
    await CreateHouse.CITY.set()


@dp.message_handler(state=CreateHouse.CITY)
async def house_city(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    answer = message.text
    await update_state(state, answer, 'city', 'create_house')
    if state_data.get('house_info'):
        await message.answer(_('Текущий адрес {address}').format(address=state_data['create_house']['address']))
    await message.answer(_('Введите адрес'))
    await CreateHouse.ADDRESS.set()


@dp.message_handler(state=CreateHouse.ADDRESS)
async def house_city(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    answer = message.text
    await update_state(state, answer, 'address', 'create_house')
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {tech}').format(tech=state_data['house_info']['tech_display']))
    await message.answer(_('Выберите технологию строительства дома'),
                         reply_markup=create_house.tech_keyboard)
    await CreateHouse.TECH.set()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_tech'), state=CreateHouse.TECH)
async def house_tech(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'tech', 'create_house')
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {terr}').format(terr=state_data['house_info']['territory_display']))
    await call.message.answer(_('Выберите тип территории'), reply_markup=create_house.terr_keyboard)
    await CreateHouse.TERR.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_terr'), state=CreateHouse.TERR)
async def house_terr(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'territory', 'create_house')
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['payment_options_display']))
    await call.message.answer(_('Выберите предпочитаемый вариант оплаты'),
                              reply_markup=create_house.payment_keyboard)
    await CreateHouse.PAYMENT_OPTIONS.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_payment'), state=CreateHouse.PAYMENT_OPTIONS)
async def house_payment(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'payment_options', 'create_house')
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['description']))
    await call.message.answer(_('Дайте описание дома'))
    await CreateHouse.DESCRIPTION.set()
    await call.answer()


@dp.message_handler(state=CreateHouse.DESCRIPTION)
async def house_city(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    answer = message.text
    await update_state(state, answer, 'description', 'create_house')
    await message.answer(_('<b>Далее идут опциональные параметры. Можете их пропустить.</b>\n' +
                           '<b>Часть из них получат стандартное значение</b>'))
    await message.answer(_('Выберите статус дома'),
                         reply_markup=create_house.role_keyboard)
    if state_data.get('house_info'):
        await message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['status_display']))
    await CreateHouse.ROLE.set()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_role'), state=CreateHouse.ROLE)
async def house_status(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'role', 'create_house')
    await call.message.answer(_('Дайте тип дома'), reply_markup=create_house.type_keyboard)
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['type_display']))
    await CreateHouse.TYPE.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_type'), state=CreateHouse.TYPE)
async def house_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'type', 'create_house')
    await call.message.answer(_('Дайте класс дома'), reply_markup=create_house.house_class_keyboard)
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['house_class_display']))
    await CreateHouse.HOUSE_CLASS.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_house_class'), state=CreateHouse.HOUSE_CLASS)
async def house_house_class(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'house_class', 'create_house')
    await call.message.answer(_('Введите расстояние до моря. Или пропустите если такового нет'))
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['create_house']['distance_to_sea']))
    await CreateHouse.SEA.set()
    await call.answer()


@dp.message_handler(state=CreateHouse.SEA)
async def house_sea(message: types.Message, state: FSMContext):
    if message.text:
        answer = message.text
        try:
            int(answer)
            await update_state(state, answer, 'distance_to_sea', 'create_house')
            state_data = await state.get_data()
            await message.answer(_('Введите высоту потолков'))
            if state_data.get('house_info'):
                await message.answer(
                    _('Сейчас: {value}').format(value=state_data['create_house']['ceiling_height']))
            await CreateHouse.HEIGHT.set()
        except ValueError:
            await message.answer(_('Введите число'))


@dp.message_handler(state=CreateHouse.HEIGHT)
async def house_height(message: types.Message, state: FSMContext):
    if message.text:
        answer = message.text
        try:
            int(answer)
            await update_state(state, answer, 'ceiling_height', 'create_house')
            state_data = await state.get_data()
            await message.answer(_('Выберите тип газопровода'), reply_markup=create_house.gas_keyboard)
            if state_data.get('house_info'):
                await message.answer(
                    _('Сейчас: {value}').format(value=state_data['house_info']['gas_display']))
            await CreateHouse.GAS.set()
        except ValueError:
            await message.answer(_('Введите число'))


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_gas'), state=CreateHouse.GAS)
async def house_gas(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'gas', 'create_house')
    await call.message.answer(_('Выберите тип отопления'), reply_markup=create_house.heating_keyboard)
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['heating_display']))
    await CreateHouse.HEATING.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_heating'), state=CreateHouse.HEATING)
async def house_heating(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'heating', 'create_house')
    await call.message.answer(_('Выберите тип электропровода'), reply_markup=create_house.electricity_keyboard)
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['electricity_display']))
    await CreateHouse.ELECTRICITY.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_electricity'), state=CreateHouse.ELECTRICITY)
async def house_electricity(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'electricity', 'create_house')
    await call.message.answer(_('Выберите тип канализации'), reply_markup=create_house.sewerage_keyboard)
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['sewerage_display']))
    await CreateHouse.SEWERAGE.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_sewerage'), state=CreateHouse.SEWERAGE)
async def house_tech(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'sewerage', 'create_house')
    await call.message.answer(_('Выберите тип водопровода'), reply_markup=create_house.water_supply_keyboard)
    if state_data.get('house_info'):
        await call.message.answer(_('Сейчас: {value}').format(value=state_data['house_info']['water_supply_display']))
    await CreateHouse.WATER.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_water'), state=CreateHouse.WATER)
async def house_water(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'water_supply', 'create_house')
    await call.message.answer(_('Далее идут дополнительные параметры'))
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) спортивная площадка?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_playground'))
    if state_data.get('house_info'):
        text = _('Есть') if state_data['house_info']['playground'] else _('Нет')
        await call.message.answer(text)
    await CreateHouse.PLAYGROUND.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_playground'), state=CreateHouse.PLAYGROUND)
async def house_playground(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'playground', 'create_house')
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) парковка?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_car_park'))
    if state_data.get('house_info'):
        text = _('Есть') if state_data['house_info']['car_park'] else _('Нет')
        await call.message.answer(text)
    await CreateHouse.CAR_PARK.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_car_park'), state=CreateHouse.CAR_PARK)
async def house_car_park(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'car_park', 'create_house')
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) магазин?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_shop'))
    if state_data.get('house_info'):
        text = _('Есть') if state_data['house_info']['shop'] else _('Нет')
        await call.message.answer(text)
    await CreateHouse.SHOP.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_shop'), state=CreateHouse.SHOP)
async def house_shop(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'shop', 'create_house')
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) детская площадка?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_child_playground'))
    if state_data.get('house_info'):
        text = _('Есть') if state_data['house_info']['child_playground'] else _('Нет')
        await call.message.answer(text)
    await CreateHouse.CHILD_PLAYGROUND.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_child_playground'),
                           state=CreateHouse.CHILD_PLAYGROUND)
async def house_child_playground(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'child_playground', 'create_house')
    await call.message.answer(_('Есть ли в вашем доме лифт?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_elevator'))
    if state_data.get('house_info'):
        text = _('Есть') if state_data['house_info']['high_speed_elevator'] else _('Нет')
        await call.message.answer(text)
    await CreateHouse.ELEVATOR.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_elevator'), state=CreateHouse.ELEVATOR)
async def house_elevator(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    value = callback_data.get('value')
    await update_state(state, value, 'high_speed_elevator', 'create_house')
    await call.message.answer(_('Есть ли в вашем доме охрана?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_security'))
    if state_data.get('house_info'):
        text = _('Есть') if state_data['house_info']['security'] else _('Нет')
        await call.message.answer(text)
    await CreateHouse.SECURITY.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_security'), state=CreateHouse.SECURITY)
async def house_security(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'security', 'create_house')
    await call.message.answer(_('Добавьте изображение дома'))
    await CreateHouse.IMAGE.set()
    await call.answer()


@dp.message_handler(state=CreateHouse.IMAGE, content_types=types.ContentType.PHOTO)
async def get_image(message: types.Message, state: FSMContext):
    images = message.photo
    image = images[-1].file_id
    await images[-1].download()
    file, created = await File.get_or_create(file_id=image,
                                             defaults={'filename': images[-1].file_id})
    await update_state(state, file.file_id, key='image', root_key='create_house')
    await message.answer(_('Подтверждаете?'), reply_markup=create_house.confirm_keyboard)
    await CreateHouse.SAVE.set()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='create_confirm'), state=CreateHouse.SAVE)
async def get_confirm_house(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    keys_to_delete = ('create_house', 'house_info')
    if value:
        data = await state.get_data()
        logging.info(data)
        house_data = data.get('create_house')
        if house_data.get('image'):
            image = await File.get(file_id=house_data.get('image'))
            image = await call.bot.get_file(image.file_id)
            if image.file_path.split('/')[-1] not in os.listdir('photos/'):
                await image.download()
            image_path = image.file_path
        else:
            image_path = 'default_form_image.png'
        with open(image_path, 'rb') as rb_image:
            house_data['image'] = rb_image
            if data.get('house_info'):
                url = f'{REL_URLS["houses"]}{data["house_info"]["id"]}/'
                resp = await Conn.patch(url, data=house_data, user_id=call.from_user.id)
                if not resp.get('id'):
                    await call.answer(_('Произошла ошибка. Повторите попытку'))
                else:
                    await call.answer(_('Информация о доме изменена'), show_alert=True)
                    new_dict = {}
                    for key, value in data.items():
                        if key not in keys_to_delete:
                            new_dict[key] = value
                    await state.finish()
                    await state.update_data(**new_dict)
            else:
                resp, status = await Conn.post(REL_URLS['houses'], data=house_data,
                                               user_id=call.from_user.id)
                if status == 201:
                    await call.answer(_('Дом создан'), show_alert=True)
                    new_dict = {}
                    for key, value in data.items():
                        if key not in keys_to_delete:
                            new_dict[key] = value
                    await state.finish()
                    await state.update_data(**new_dict)
                else:
                    await call.answer(_('Произошла ошибка. Повторите попытке'))
                    if resp.get('Error'):
                        await call.answer(resp.get('Error'))
    else:
        await call.answer(_('Вы можете выбрать нужные этап через меню'))
