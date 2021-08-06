import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from states.state_groups import CreateHouse

from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline import create_house

from middlewares import _

from typing import Union

from utils.db_api.models import File
from utils.session.url_dispatcher import REL_URLS


async def update_state(state: FSMContext, new_data: Union[int, str, dict],
                       key: str):
    data = await state.get_data()
    house_data = data.get('create_house')
    house_data[key] = new_data
    await state.update_data(create_house=house_data)


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreateHouse)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    if data.get('create_house'):
        data.pop('create_house')
    await state.finish()
    data['path'] = path
    await state.update_data(**data)


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
    answer = message.text
    await update_state(state, answer, 'name')
    await message.answer(_('Введите город'))
    await CreateHouse.CITY.set()


@dp.message_handler(state=CreateHouse.CITY)
async def house_city(message: types.Message, state: FSMContext):
    answer = message.text
    await update_state(state, answer, 'city')
    await message.answer(_('Введите адрес'))
    await CreateHouse.ADDRESS.set()


@dp.message_handler(state=CreateHouse.ADDRESS)
async def house_city(message: types.Message, state: FSMContext):
    answer = message.text
    await update_state(state, answer, 'address')
    await message.answer(_('Выберите технологию строительства дома'),
                         reply_markup=create_house.tech_keyboard)
    await CreateHouse.TECH.set()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_tech'), state=CreateHouse.TECH)
async def house_tech(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'tech')
    await call.message.answer(_('Выберите тип территории'), reply_markup=create_house.terr_keyboard)
    await CreateHouse.TERR.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_terr'), state=CreateHouse.TERR)
async def house_terr(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'territory')
    await call.message.answer(_('Выберите предпочитаемый вариант оплаты'),
                              reply_markup=create_house.payment_keyboard)
    await CreateHouse.PAYMENT_OPTIONS.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_payment'), state=CreateHouse.PAYMENT_OPTIONS)
async def house_payment(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'payment_options')
    await call.message.answer(_('Дайте описание дома'))
    await CreateHouse.DESCRIPTION.set()
    await call.answer()


@dp.message_handler(state=CreateHouse.DESCRIPTION)
async def house_city(message: types.Message, state: FSMContext):
    answer = message.text
    await update_state(state, answer, 'description')
    await message.answer(_('<b>Далее идут опциональные параметры. Можете их пропустить.</b>\n' +
                           '<b>Часть из них получат стандартное значение</b>'))
    await message.answer(_('Выберите статус дома'),
                         reply_markup=create_house.role_keyboard)
    await CreateHouse.ROLE.set()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_role'), state=CreateHouse.ROLE)
async def house_status(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'role')
    await call.message.answer(_('Дайте тип дома'), reply_markup=create_house.type_keyboard)
    await CreateHouse.TYPE.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_type'), state=CreateHouse.TYPE)
async def house_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'type')
    await call.message.answer(_('Дайте класс дома'), reply_markup=create_house.house_class_keyboard)
    await CreateHouse.HOUSE_CLASS.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_house_class'), state=CreateHouse.HOUSE_CLASS)
async def house_house_class(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'house_class')
    await call.message.answer(_('Введите расстояние до моря. Или пропустите если такового нет'))
    await CreateHouse.SEA.set()
    await call.answer()


@dp.message_handler(state=CreateHouse.SEA)
async def house_sea(message: types.Message, state: FSMContext):
    if message.text:
        answer = message.text
        await update_state(state, answer, 'distance_to_sea')
    await message.answer(_('Введите высоту потолков'))
    await CreateHouse.HEIGHT.set()


@dp.message_handler(state=CreateHouse.HEIGHT)
async def house_height(message: types.Message, state: FSMContext):
    if message.text:
        answer = message.text
        await update_state(state, answer, 'ceiling_height')
    await message.answer(_('Выберите тип газопровода'), reply_markup=create_house.gas_keyboard)
    await CreateHouse.GAS.set()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_gas'), state=CreateHouse.GAS)
async def house_gas(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'gas')
    await call.message.answer(_('Выберите тип отопления'), reply_markup=create_house.heating_keyboard)
    await CreateHouse.HEATING.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_heating'), state=CreateHouse.HEATING)
async def house_heating(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'heating')
    await call.message.answer(_('Выберите тип электропровода'), reply_markup=create_house.electricity_keyboard)
    await CreateHouse.ELECTRICITY.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_electricity'), state=CreateHouse.ELECTRICITY)
async def house_electricity(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'electricity')
    await call.message.answer(_('Выберите тип канализации'), reply_markup=create_house.sewerage_keyboard)
    await CreateHouse.SEWERAGE.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_sewerage'), state=CreateHouse.SEWERAGE)
async def house_tech(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'sewerage')
    await call.message.answer(_('Выберите тип водопровода'), reply_markup=create_house.water_supply_keyboard)
    await CreateHouse.WATER.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_water'), state=CreateHouse.WATER)
async def house_water(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'water_supply')
    await call.message.answer(_('Далее идут дополнительные параметры'))
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) спортивная площадка?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_playground'))
    await CreateHouse.PLAYGROUND.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_playground'), state=CreateHouse.PLAYGROUND)
async def house_playground(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'playground')
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) парковка?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_car_park'))
    await CreateHouse.CAR_PARK.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_car_park'), state=CreateHouse.CAR_PARK)
async def house_car_park(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'car_park')
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) магазин?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_shop'))
    await CreateHouse.SHOP.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_shop'), state=CreateHouse.SHOP)
async def house_shop(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'shop')
    await call.message.answer(_('Есть ли в вашем доме(или рядом с ним) детская площадка?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_child_playground'))
    await CreateHouse.CHILD_PLAYGROUND.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_child_playground'),
                           state=CreateHouse.CHILD_PLAYGROUND)
async def house_child_playground(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'child_playground')
    await call.message.answer(_('Есть ли в вашем доме лифт?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_elevator'))
    await CreateHouse.ELEVATOR.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_elevator'), state=CreateHouse.ELEVATOR)
async def house_elevator(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'elevator')
    await call.message.answer(_('Есть ли в вашем доме охрана?'),
                              reply_markup=await create_house.get_advantages_keyboard('add_security'))
    await CreateHouse.SECURITY.set()
    await call.answer()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='add_security'), state=CreateHouse.SECURITY)
async def house_security(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'security')
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
    await update_state(state, file.file_id, key='image')
    await message.answer(_('Подтверждаете?'), reply_markup=create_house.confirm_keyboard)
    await CreateHouse.SAVE.set()


@dp.callback_query_handler(create_house.ITEM_CB.filter(action='create_confirm'), state=CreateHouse.SAVE)
async def get_confirm_house(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    if value:
        data = await state.get_data()
        logging.info(data)
        house_data = data.get('create_house')
        image = await File.get(file_id=house_data.get('image'))
        image = await call.bot.get_file(image.file_id)
        with open(image.file_path, 'rb') as rb_image:
            house_data['image'] = rb_image
            resp, status = await Conn.post(REL_URLS['houses'], data=house_data,
                                           user_id=call.from_user.id)
            if status == 201:
                await call.answer(_('Дом создан'), show_alert=True)
                data.pop('create_house')
                await state.finish()
                await state.update_data(**data)
            else:
                await call.answer(_('Произошла ошибка. Повторите попытке'))
                if resp.get('Error'):
                    await call.answer(resp.get('Error'))
    else:
        await call.answer(_('Вы можете выбрать нужные этап через меню'))
