import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from loader import dp, Conn, log

from keyboards.callbacks.user_callback import DETAIL_CB, POST_FILTER_CB
from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline import create_flat
from keyboards.inline.create_house import confirm_keyboard
from utils.db_api.models import File

from utils.session.url_dispatcher import REL_URLS
from states.state_groups import CreateFlat

from handlers.users.utils import update_state

from middlewares import _


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreateFlat)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    keys_to_delete = ('create_flat', 'flat_info', 'house_pk')
    new_dict = {}
    for key, value in data.items():
        if key not in keys_to_delete:
            new_dict[key] = value
    await state.finish()
    new_dict['path'] = path
    await state.update_data(**new_dict)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=CreateFlat)
async def save_flat(message: types.Message, state: FSMContext):
    data = await state.get_data()
    flat_data = data.get('create_flat')
    keys = ('number', 'square', 'kitchen_square', 'price', 'price_per_metre',
            'number_of_rooms', 'state', 'foundation_doc', 'type', 'plan',
            'balcony', 'schema', 'floor')
    if all(key in flat_data for key in keys):
        await message.answer(_('Подтверждаете?'),
                             reply_markup=confirm_keyboard)
        await CreateFlat.SAVE.set()
    else:
        text = _('Вы не указали: \n')
        if not flat_data.get('number'):
            text += _('Номер\n')
        if not flat_data.get('square'):
            text += _('Площадь\n')
        if not flat_data.get('kitchen_square'):
            text += _('Площадь кухни')
        if not flat_data.get('price'):
            text += _('Цену')
        if not flat_data.get('price_per_metre'):
            text += _('Цену за кв. метр')
        if not flat_data.get('number_of_rooms'):
            text += _('Количество комнат')
        if not flat_data.get('state'):
            text += _('Состояние')
        if not flat_data.get('foundation_doc'):
            text += _('Формат собственности')
        if not flat_data.get('type'):
            text += _('Тип')
        if not flat_data.get('plan'):
            text += _('Планировку')
        if not flat_data.get('balcony'):
            text += _('Наличие или отсутствие балкона')
        if not flat_data.get('schema'):
            text += _('Схему квартиры')
        await message.answer(text)


@dp.message_handler(Text(equals=['Перейти к этажу', 'Go to floor']), state=CreateFlat)
async def go_to_flat_floor(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    floor_resp = await Conn.get(REL_URLS['floors'],
                                params={'house': state_data['house_pk']},
                                user_id=message.from_user.id)
    floor_keyboard = await create_flat.get_floors_keyboard(floor_resp['results'])
    text = ''
    for index, item in enumerate(floor_resp, start=1):
        text += f'{index}. {item["floor_full_name "]}'
    await message.answer(_('Выберите этаж'), reply_markup=floor_keyboard)
    if state_data['flat_info']:
        await message.answer(_('\nСейчас: {value}').format(value=state_data['flat_info']['flat_display']))
    await CreateFlat.FLOOR.set()


@dp.message_handler(Text(equals=['Перейти к номеру', 'Go to number']), state=CreateFlat)
async def go_to_flat_number(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите номер')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['create_flat']['number'])
    await message.answer(text)
    await CreateFlat.NUMBER.set()


@dp.message_handler(Text(equals=['Перейти к площади', 'Go to square']), state=CreateFlat)
async def go_to_flat_square(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите площадь')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['create_flat']['square'])
    await message.answer(text)
    await CreateFlat.SQUARE.set()


@dp.message_handler(Text(equals=['Перейти к площади кухни', 'Go to kitchen square']), state=CreateFlat)
async def go_to_flat_kitchen_square(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите площадь кухни')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['create_flat']['kitchen_square'])
    await message.answer(text)
    await CreateFlat.KITCHEN_SQUARE.set()


@dp.message_handler(Text(equals=['Перейти к цене', 'Go to price']), state=CreateFlat)
async def go_to_flat_price(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите цену')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['create_flat']['price'])
    await message.answer(text)
    await CreateFlat.PRICE.set()


@dp.message_handler(Text(equals=['Перейти к цене за кв. метр', 'Go to price per metre']), state=CreateFlat)
async def go_to_flat_price_per_metre(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите цену за квадратный метр')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['create_flat']['price_per_metre'])
    await message.answer(text)
    await CreateFlat.PRICE_PER_METRE.set()


@dp.message_handler(Text(equals=['Перейти к числу комнат', 'Go to number of rooms']), state=CreateFlat)
async def go_to_flat_number_of_rooms(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите число комнат')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['create_flat']['number_of_rooms'])
    await message.answer(text)
    await CreateFlat.ROOMS.set()


@dp.message_handler(Text(equals=['Перейти к состоянию', 'Go to state']), state=CreateFlat)
async def go_to_flat_state(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите состояние')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['flat_info']['state_display'])
    await message.answer(text, reply_markup=create_flat.state_keyboard)
    await CreateFlat.STATE.set()


@dp.message_handler(Text(equals=['Перейти к типу собственности', 'Go to foundation document']), state=CreateFlat)
async def go_to_flat_foundation_doc(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите формат собственности')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['flat_info']['foundation_doc_display'])
    await message.answer(text, reply_markup=create_flat.foundation_doc_keyboard)
    await CreateFlat.DOC.set()


@dp.message_handler(Text(equals=['Перейти к типу', 'Go to type']), state=CreateFlat)
async def go_to_flat_type(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Укажите тип')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['flat_info']['type_display'])
    await message.answer(text, reply_markup=create_flat.flat_type_keyboard)
    await CreateFlat.TYPE.set()


@dp.message_handler(Text(equals=['Перейти к балкону', 'Go to balcony']), state=CreateFlat)
async def go_to_flat_balcony(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = _('Есть ли балкон/лоджия?')
    if state_data['flat_info']:
        text += _('\nСейчас: {value}').format(value=state_data['flat_info']['balcony_display'])
    await message.answer(text, reply_markup=create_flat.balcony_keyboard)
    await CreateFlat.BALCONY.set()


@dp.message_handler(Text(equals=['Перейти к схеме', 'Go to schema']), state=CreateFlat)
async def go_to_flat_schema(message: types.Message):
    text = _('Загрузие схему квартиры')
    await message.answer(text)
    await CreateFlat.SCHEMA.set()


@dp.callback_query_handler(DETAIL_CB.filter(action='edit_flat'))
async def edit_flat(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["flats_public"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    image_name = resp.get('schema').split('/')[-1]
    file = await File.get(filename=image_name)
    if image_name not in os.listdir('photos/'):
        bot_file = await call.bot.get_file(file.file_id)
        await bot_file.download()
        file.file_path = bot_file.file_path
        await file.save()
    flat_data = {
        'floor': str(resp.get('floor')),
        'number': str(resp.get('number')),
        'square': str(resp.get('square')),
        'kitchen_square': str(resp.get('kitchen_square')),
        'price': str(resp.get('price')),
        'price_per_metre': str(resp.get('price_per_metre')),
        'number_of_rooms': str(resp.get('number_of_rooms')),
        'state': resp.get('state'),
        'foundation_doc': resp.get('foundation_doc'),
        'type': resp.get('type'),
        'plan': resp.get('plan'),
        'balcony': resp.get('balcony'),
        'heating': resp.get('heating'),
        'schema': file.file_id
    }
    floor_resp = await Conn.get(REL_URLS['floors'], params={'house': resp['house_pk']}, user_id=call.from_user.id)
    keyboard, path = await dispatcher('LEVEL_4_ADD_FLAT', user_id=call.from_user.id)
    await call.message.answer(_('Редактируте информацию. \nВыберите этаж. \n' +
                                'Сейчас: {floor}').format(floor=resp.get('floor_display')),
                              reply_markup=keyboard)
    log.debug({'path': path})
    keyboard = await create_flat.get_floors_keyboard(floor_resp['results'])
    text = ''
    for index, item in enumerate(floor_resp['results'], start=1):
        text += f'{index}. {item["floor_full_name"]}\n'
    await call.message.answer(text, reply_markup=keyboard)
    await CreateFlat.FLOOR.set()
    await state.update_data(path=path, flat_info=resp, create_flat=flat_data)
    await call.answer()


@dp.callback_query_handler(DETAIL_CB.filter(action='add_flat'))
async def add_flat(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await CreateFlat.STARTER.set()
    pk = callback_data.get('pk')
    keyboard, path = await dispatcher('LEVEL_4_ADD_FLAT', user_id=call.from_user.id)
    floor_resp = await Conn.get(REL_URLS['floors'], params={'house': pk}, user_id=call.from_user.id)
    floors = floor_resp.get('results')
    if floors:
        floor_keyboard = await create_flat.get_floors_keyboard(floor_resp['results'])
        text = ''
        for index, item in enumerate(floor_resp['results'], start=1):
            text += f'{index}. {item["floor_full_name"]}'
        await call.message.answer(_('Выберите этаж'), reply_markup=keyboard)
        await call.message.answer(text, reply_markup=floor_keyboard)
        await CreateFlat.FLOOR.set()
        await state.update_data(path=path, create_flat={}, house_pk=pk)
    else:
        await call.answer(_('Нет этажей. Добавьте их сперва'))
        state_data = await state.get_data()
        await state.finish()
        await state.update_data(**state_data)


@dp.callback_query_handler(POST_FILTER_CB.filter(action='add_floor'), state=CreateFlat.FLOOR)
async def flat_floor(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    state_data = await state.get_data()
    await update_state(state, value, 'floor', 'create_flat')
    text = _('Укажите номер квартиры')
    if state_data.get('flat_info'):
        text += _('Сейчас: {value}').format(value=state_data['flat_info']['number'])
    await call.message.answer(text)
    await CreateFlat.NUMBER.set()
    await call.answer()


@dp.message_handler(state=CreateFlat.NUMBER)
async def flat_number(message: types.Message, state: FSMContext):
    try:
        int(message.text)
        await update_state(state, new_data=message.text, key='number', root_key='create_flat')
        text = _('Введите площадь квартиры')
        state_data = await state.get_data()
        if state_data.get('flat_info'):
            text += _('\nТекущая площадь - {value}').format(value=state_data['create_flat']['square'])
        await message.answer(text)
        await CreateFlat.SQUARE.set()
    except ValueError:
        await message.answer(_('Введите <b>номер</b>'))


@dp.message_handler(state=CreateFlat.SQUARE)
async def flat_square(message: types.Message, state: FSMContext):
    try:
        int(message.text)
        await update_state(state, new_data=message.text, key='square', root_key='create_flat')
        text = _('Введите площадь кухни')
        state_data = await state.get_data()
        if state_data.get('flat_info'):
            text += _('\nТекущая площадь кухни - {value}').format(value=state_data['create_flat']['kitchen_square'])
        await message.answer(text)
        await CreateFlat.KITCHEN_SQUARE.set()
    except ValueError:
        await message.answer(_('Введите <b>номер</b>'))


@dp.message_handler(state=CreateFlat.KITCHEN_SQUARE)
async def flat_kitchen_square(message: types.Message, state: FSMContext):
    try:
        int(message.text)
        await update_state(state, new_data=message.text, key='kitchen_square', root_key='create_flat')
        text = _('Введите цену')
        state_data = await state.get_data()
        if state_data.get('flat_info'):
            text += _('\nТекущая цена - {value}').format(value=state_data['create_flat']['price'])
        await message.answer(text)
        await CreateFlat.PRICE.set()
    except ValueError:
        await message.answer(_('Введите <b>номер</b>'))


@dp.message_handler(state=CreateFlat.PRICE)
async def flat_price(message: types.Message, state: FSMContext):
    try:
        int(message.text)
        await update_state(state, new_data=message.text, key='price', root_key='create_flat')
        text = _('Введите цену за квадратный метр')
        state_data = await state.get_data()
        if state_data.get('flat_info'):
            text += _('\nТекущая цена за кв.м- {value}').format(value=state_data['create_flat']['price_per_metre'])
        await message.answer(text)
        await CreateFlat.PRICE_PER_METRE.set()
    except ValueError:
        await message.answer(_('Введите <b>номер</b>'))


@dp.message_handler(state=CreateFlat.PRICE_PER_METRE)
async def flat_price_pre_metre(message: types.Message, state: FSMContext):
    try:
        int(message.text)
        await update_state(state, new_data=message.text, key='price_per_metre', root_key='create_flat')
        text = _('Введите количество комнат')
        state_data = await state.get_data()
        if state_data.get('flat_info'):
            text += _('\nТекущая количество - {value}').format(value=state_data['create_flat']['number_of_rooms'])
        await message.answer(text)
        await CreateFlat.ROOMS.set()
    except ValueError:
        await message.answer(_('Введите <b>номер</b>'))


@dp.message_handler(state=CreateFlat.ROOMS)
async def flat_rooms(message: types.Message, state: FSMContext):
    try:
        int(message.text)
        await update_state(state, new_data=message.text, key='number_of_rooms', root_key='create_flat')
        text = _('Укажите состояние квартиры')
        state_data = await state.get_data()
        if state_data.get('flat_info'):
            text += _('\nТекущее состояние - {value}').format(value=state_data['flat_info']['state'])
        await message.answer(text, reply_markup=create_flat.state_keyboard)
        await CreateFlat.STATE.set()
    except ValueError:
        await message.answer(_('Введите <b>номер</b>'))


@dp.callback_query_handler(POST_FILTER_CB.filter(action='add_state'), state=CreateFlat.STATE)
async def flat_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'state', 'create_flat')
    text = _('Укажите формат собственности')
    state_data = await state.get_data()
    if state_data.get('flat_info'):
        text += _('\nТекущий формат - {value}').format(value=state_data['flat_info']['foundation_doc'])
    await call.message.answer(text, reply_markup=create_flat.foundation_doc_keyboard)
    await CreateFlat.DOC.set()
    await call.answer()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='add_doc'), state=CreateFlat.DOC)
async def flat_doc(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'foundation_doc', 'create_flat')
    text = _('Укажите тип')
    state_data = await state.get_data()
    if state_data.get('flat_info'):
        text += _('\nТекущий тип - {value}').format(value=state_data['flat_info']['type'])
    await call.message.answer(text, reply_markup=create_flat.flat_type_keyboard)
    await CreateFlat.TYPE.set()
    await call.answer()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='add_type'), state=CreateFlat.TYPE)
async def flat_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'type', 'create_flat')
    text = _('Укажите планировку')
    state_data = await state.get_data()
    if state_data.get('flat_info'):
        text += _('\nТекущая планировка - {value}').format(value=state_data['flat_info']['plan'])
    await call.message.answer(text, reply_markup=create_flat.plan_keyboard)
    await CreateFlat.PLAN.set()
    await call.answer()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='add_plan'), state=CreateFlat.PLAN)
async def flat_plan(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'plan', 'create_flat')
    text = _('Есть ли балкон/лоджия?')
    state_data = await state.get_data()
    if state_data.get('flat_info'):
        text += _('\nСейчас - {value}').format(value=state_data['flat_info']['balcony'])
    await call.message.answer(text, reply_markup=create_flat.balcony_keyboard)
    await CreateFlat.BALCONY.set()
    await call.answer()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='add_balcony'), state=CreateFlat.BALCONY)
async def flat_balcony(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'balcony', 'create_flat')
    await call.message.answer(_('Загрузите схему квартиры'))
    await CreateFlat.SCHEMA.set()
    await call.answer()


@dp.message_handler(state=CreateFlat.SCHEMA, content_types=types.ContentType.PHOTO)
async def flat_schema(message: types.Message, state: FSMContext):
    images = message.photo
    image = images[-1].file_id
    await images[-1].download()
    file, created = await File.get_or_create(file_id=image,
                                             defaults={'filename': images[-1].file_id})
    await update_state(state, file.file_id, 'schema', 'create_flat')
    await message.answer(_('Подтверждаете?'), reply_markup=confirm_keyboard)
    await CreateFlat.SAVE.set()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='create_confirm'), state=CreateFlat.SAVE)
async def flat_save(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    keys_to_delete = ('create_flat', 'flat_info', 'house_pk')
    if value:
        data = await state.get_data()
        log.info(data)
        flat_data = data.get('create_flat')
        schema = await File.get(file_id=flat_data.get('schema'))
        if not schema.file_path:
            image = await call.bot.get_file(schema.file_id)
            await image.download()
            schema.file_path = image.file_path
            await schema.save()
        with open(schema.file_path, 'rb') as rb_image:
            flat_data['schema'] = rb_image
            if data.get('flat_info'):
                url = f'{REL_URLS["flats"]}{data["flat_info"]["id"]}/'
                resp = await Conn.patch(url, data=flat_data, user_id=call.from_user.id)
                if not resp.get('id'):
                    await call.answer(_('Произошла ошибка попробуйте снова'))
                else:
                    await call.answer(_('Информация о квартире изменена'), show_alert=True)
                    new_dict = {}
                    for key, value in data.items():
                        if key not in keys_to_delete:
                            new_dict[key] = value
                    await state.finish()
                    await state.update_data(**new_dict)
            else:
                resp, status = await Conn.post(REL_URLS['flats'], data=flat_data, user_id=call.from_user.id)
                if status == 201:
                    await call.answer(_('Квартира добавлена'), show_alert=True)
                    new_dict = {}
                    for key, value in data.items():
                        if key not in keys_to_delete:
                            new_dict[key] = value
                    await state.finish()
                    await state.update_data(**new_dict)
                    await state.finish()
                    await state.update_data(**new_dict)
                else:
                    await call.answer(_('Произошла ошибка. Повторите попытке'))
    else:
        await call.answer(_('Вы можете выбрать нужные этап через меню'))
