from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn, log

from states.state_groups import CreatePost
from deserializers.post import HouseForCreatePost, BaseDeserializer, FlatForCreatePost, PostDeserializer

from middlewares import _

from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline.create_post import (ITEM_CB, get_item_for_create_post, get_payment_options,
                                          get_communication_keyboard, get_create_post_confirm_keyboard)
from keyboards.callbacks.user_callback import DETAIL_CB

from utils.session.url_dispatcher import REL_URLS
from utils.db_api.models import File

from handlers.users.utils import update_state

import os

from typing import Optional


house_des = HouseForCreatePost()
flat_des = FlatForCreatePost()
post_des = PostDeserializer()


async def list_items(user_id: int, url: str, deserializer: BaseDeserializer,
                     keyboard, error_text: str, action: str, params: Optional[dict] = None):
    resp = await Conn.get(url, user_id=user_id, params=params)
    if resp.get('results'):
        if action == 'add_house':
            new_resp = {'results': []}
            for item in resp['results']:
                if item.get('flat_count') > 0:  # If house doesnt have flats - wont display this house
                    new_resp['results'].append(item)
            resp = new_resp
            if not resp:
                _('У вас нет домов с квартирами'), keyboard([]), False
        data = await deserializer.make_list(resp)
        text = ''
        for index, item in enumerate(data, start=1):
            text += f'{index}. {item.data}\n'
        return text, keyboard(data, action), True
    else:
        return error_text, keyboard([]), False


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreatePost)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    keys_to_delete = ('create_post', 'post_info')
    new_dict = {}
    for key, value in data.items():
        if key not in keys_to_delete:
            new_dict[key] = value
    await state.finish()
    new_dict['path'] = path
    await state.update_data(**new_dict)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=CreatePost)
async def save_post_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get('create_post')
    keys = ('house', 'flat', 'payment_options', 'communications',
            'price', 'description', 'main_image')
    if all(key in post_data for key in keys):
        text = _('Подтверждаете?')
        await message.answer(text, reply_markup=await get_create_post_confirm_keyboard())
        await CreatePost.SAVE.set()
    else:
        text = _('Вы не указали: \n')
        if not post_data.get('house'):
            text += _('Дом\n')
        if not post_data.get('flat'):
            text += _('Квартиру\n')
        if not post_data.get('payment_options'):
            text += _('Метод оплаты\n')
        if not post_data.get('price'):
            text += _('Цену\n')
        if not post_data.get('communications'):
            text += _('Способ коммуникации с вами\n')
        if not post_data.get('description'):
            text += _('Описание\n')
        if not post_data.get('main_image'):
            text += _('Фото к объявлению\n')
        await message.answer(text)


@dp.message_handler(Text(equals=['Перейти к дому', 'Go to house']), state=CreatePost)
async def go_to_house(message: types.Message, state: FSMContext):
    data = await state.get_data()
    error_text = _('Домов нет. Добавьте дом, преждем чем создавать объявление')
    text, keyboard_cor, status = await list_items(user_id=message.from_user.id,
                                                  url=REL_URLS['houses'],
                                                  deserializer=house_des,
                                                  keyboard=get_item_for_create_post,
                                                  error_text=error_text,
                                                  action='add_house')
    if not status:
        await message.answer(text)
        keyboard_cor.close()
        return
    await message.answer(_('Выберите дом'))
    if data.get('post_info'):
        await message.answer(_('Сейчас: {value}').format(value=data['post_info']['house']))
    await message.answer(text, reply_markup=await keyboard_cor)
    await CreatePost.HOUSE.set()


@dp.message_handler(Text(equals=['Перейти к квартире', 'Go to flat']), state=CreatePost)
async def go_to_flat(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('create_house') or not data['create_house'].get('house'):
        await message.answer(_('Сперва выберите дом'))
        return
    params = {'house_pk': data['create_house']['house']}
    error_text = _('Квартир нет. Добавьте квартиру, преждем чем создавать объявление')
    text, keyboard_cor, status = await list_items(user_id=message.from_user.id,
                                                  url=REL_URLS['flats_public'],
                                                  deserializer=flat_des,
                                                  keyboard=get_item_for_create_post,
                                                  error_text=error_text,
                                                  action='add_flat',
                                                  params=params)
    if not status:
        await message.answer(text)
        keyboard_cor.close()
        return
    await message.answer(_('Выберите квартиру'))
    if data.get('post_info'):
        await message.answer(_('Сейчас: {value}').format(value=data['post_info']['flat']))
    await message.answer(text, reply_markup=await keyboard_cor)
    await CreatePost.FLAT.set()


@dp.message_handler(Text(equals=['Перейти к цене', 'Go to price']), state=CreatePost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get('create_post')
    if data.get('post_info'):
        current_price = data['post_info']['price']
    else:
        current_price = post_data.get('price', _('Не указано'))
    await message.answer(_('Текущая цена: {price}\n' +
                           'Введите новую цену').format(price=current_price))
    await CreatePost.PRICE.set()


@dp.message_handler(Text(equals=['Перейти к способу платежа', 'Go to payment options']), state=CreatePost)
async def go_to_payment_option(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('post_info'):
        await message.answer(_('Сейчас: {value}').format(value=data['post_info']['payment']))
    await message.answer(_('Выберите метод оплаты'),
                         reply_markup=await get_payment_options())
    await CreatePost.PAYMENT.set()


@dp.message_handler(Text(equals=['Перейти к вариантам связи', 'Go to communication']), state=CreatePost)
async def go_to_communications(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('post_info'):
        await message.answer(_('Сейчас: {value}').format(value=data['post_info']['communication']))
    await message.answer(_('Выберите метод коммуникации'), reply_markup=await get_communication_keyboard())
    await CreatePost.COMMUNICATION.set()


@dp.message_handler(Text(equals=['Перейти к описанию', 'Go to description']), state=CreatePost)
async def go_to_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get('create_post')
    if post_data:
        current_desc = post_data.get('description', _('Не указано'))
        await message.answer(_('Текущее описание\n {desc}').format(desc=current_desc))
    if data.get('post_info'):
        current_desc = data['post_info']['description'] or _('Не указано')
    await message.answer('Добавьте описание')
    await CreatePost.DESCRIPTION.set()


@dp.message_handler(Text(equals=['Перейти к фото', 'Go to photo']), state=CreatePost)
async def go_to_photo(message: types.Message):
    await message.answer(_('Добавьте изображение'))
    await CreatePost.IMAGE.set()


@dp.callback_query_handler(DETAIL_CB.filter(action='edit_post'))
async def edit_post(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    pk = callback_data.get('pk')
    url = f'{REL_URLS["posts_public"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    post_data_display = {
        'pk': resp['id'],
        'house': resp['house'],
        'flat': resp['flat_info']['floor'],
        'payment': resp['payment_options_display'],
        'price': resp['price'],
        'communication': resp['communications_display'],
        'description': resp['description'] or '',
    }
    image_name = resp.get('main_image').split('/')[-1]
    file = await File.get(filename=image_name)
    if image_name not in os.listdir('photos/'):
        bot_file = await call.bot.get_file(file.file_id)
        await bot_file.download()
        file.file_path = bot_file.file_path
        await file.save()
    post_data = {
        'house': str(resp['house']),
        'flat': str(resp['flat']),
        'payment_options': resp['payment_options'],
        'price': str(resp['price']),
        'communications': resp['communications'],
        'description': resp['description'],
        'main_image': file.file_id
    }
    inst = await post_des.for_detail(resp)
    url_house = f'{REL_URLS["houses_public"]}{post_data_display["house"]}/'
    house_rep = await Conn.get(url_house, user_id=call.from_user.id)
    post_data_display['house'] = house_rep['name']
    keyboard, path = await dispatcher('LEVEL_3_CREATE_POST', call.from_user.id)
    await call.message.answer(inst.data)
    await call.message.answer(_('Редактируйте информацию'),
                              reply_markup=keyboard)
    log.info({'path': path})
    error_text = _('Домов нет. Добавьте дом, преждем чем создавать объявление')
    text, keyboard_cor, status = await list_items(user_id=call.from_user.id,
                                                  url=REL_URLS['houses'],
                                                  deserializer=house_des,
                                                  keyboard=get_item_for_create_post,
                                                  error_text=error_text,
                                                  action='add_house')
    if not status:
        await call.message.answer(text)
        keyboard_cor.close()
        return
    await call.message.answer(_('Выберите дом\n' +
                                'Сейчас {house}').format(house=post_data['house']))
    await call.message.answer(text, reply_markup=await keyboard_cor)
    await CreatePost.HOUSE.set()
    await state.update_data(path=path, post_info=post_data_display, create_post=post_data)
    await call.answer()


@dp.message_handler(Text(equals=['Добавить новую публикацию', 'Add new post']))
async def add_post(message: types.Message, state: FSMContext):
    await CreatePost.STARTER.set()
    keyboard, path = await dispatcher('LEVEL_3_CREATE_POST', message.from_user.id)
    await message.answer(_('Заполните форму для создания объявления'),
                         reply_markup=keyboard)
    await state.update_data(path=path)
    log.info({'path': path})
    error_text = _('Домов нет. Добавьте дом, преждем чем создавать объявление')
    text, keyboard_cor, status = await list_items(user_id=message.from_user.id,
                                                  url=REL_URLS['houses'],
                                                  deserializer=house_des,
                                                  keyboard=get_item_for_create_post,
                                                  error_text=error_text,
                                                  action='add_house')
    if not status:
        await message.answer(text)
        keyboard_cor.close()
        return
    await message.answer(_('Выберите дом'))
    await message.answer(text, reply_markup=await keyboard_cor)
    await CreatePost.HOUSE.set()
    await state.update_data(create_post={})


@dp.callback_query_handler(DETAIL_CB.filter(action='add_house'), state=CreatePost.HOUSE)
async def add_house(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    log.info(callback_data)
    pk = callback_data.get('pk')
    url = f'{REL_URLS["houses"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    if resp:
        data = await house_des.for_detail(resp)
        text = _('Выбранный дом:\n' +
                 data.data)
        await call.message.answer(text)
        await update_state(state, new_data=pk, key='house', root_key='create_post')
        await call.answer()

        error_text = _('Квартир нет. Добавьте квартиру, преждем чем работать с объявлением')
        text, keyboard_cor, status = await list_items(user_id=call.from_user.id,
                                                      url=REL_URLS['flats_public'],
                                                      deserializer=flat_des,
                                                      keyboard=get_item_for_create_post,
                                                      error_text=error_text,
                                                      action='add_flat',
                                                      params={'house__pk': str(pk)})
        if not status:
            await call.message.answer(text)
            keyboard_cor.close()
            return
        await call.message.answer(_('Выберите квартиру'))
        if state_data.get('post_info'):
            text = _('Сейчас: {flat}').format(flat=state_data['post_info']['flat'])
            await call.message.answer(text)
        if not text:
            await call.message.answer(_('В этом доме ещё нет квартир'))
            keyboard_cor.close()
            return
        await call.message.answer(text, reply_markup=await keyboard_cor)
        await CreatePost.FLAT.set()
    else:
        await call.answer(_('Такого дома нет в системе. Выберите другой'))


@dp.callback_query_handler(DETAIL_CB.filter(action='add_flat'), state=CreatePost.FLAT)
async def get_flat(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    log.debug(callback_data)
    state_data = await state.get_data()
    pk = callback_data.get('pk')
    url = f'{REL_URLS["flats"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    if resp:
        data = await flat_des.for_detail(resp)
        text = _('Выбранная квартира:\n' +
                 data.data)
        await call.message.answer(text)
        await update_state(state, new_data=pk, key='flat', root_key='create_post')
        await call.answer()

        await call.message.answer(_('Выберите метод оплаты'), reply_markup=await get_payment_options())
        if state_data.get('post_info'):
            await call.message.answer(_('Сейчас: {value}').format(value=state_data['post_info']['payment']))
        await CreatePost.PAYMENT.set()
    else:
        await call.answer(_('Нет такой квартиры в системе. Выберите другую'))


@dp.callback_query_handler(ITEM_CB.filter(action='add_payment'), state=CreatePost.PAYMENT)
async def get_payment(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    log.debug(callback_data)
    value = callback_data.get('value')
    await update_state(state, new_data=value, key='payment_options', root_key='create_post')
    await call.answer(_('Метод оплаты добавлен'))
    await call.message.answer(_('Введите цену'))
    if state_data.get('post_info'):
        await call.message.answer(_('Сейчас {price}').format(state_data['post_info']['price']))
    await CreatePost.PRICE.set()


@dp.message_handler(state=CreatePost.PRICE)
async def get_price(message: types.Message, state: FSMContext):
    value = message.text
    try:
        state_data = await state.get_data()
        value = value.replace(' ', '')
        await update_state(state, new_data=value, key='price', root_key='create_post')
        await message.answer(_('Цена добавлена'))
        await message.answer(_('Выберите метод коммуникации'), reply_markup=await get_communication_keyboard())
        if state_data.get('post_info'):
            await message.answer(_('Сейчас: {value}').format(value=state_data['post_info']['communication']))
        await CreatePost.COMMUNICATION.set()
    except ValueError:
        await message.answer(_('Неправильный формат ввода'))


@dp.callback_query_handler(ITEM_CB.filter(action='add_comm'), state=CreatePost.COMMUNICATION)
async def get_communication(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    log.debug(callback_data)
    value = callback_data.get('value')
    state_data = await state.get_data()
    await update_state(state, new_data=value, key='communications', root_key='create_post')
    await call.answer(_('Способ связи добавлен'))
    await call.message.answer('Добавьте описание')
    if state_data.get('post_info'):
        await call.message.answer(_('Сейчас:\n {desc}').format(desc=state_data['post_info']['description']))
    await CreatePost.DESCRIPTION.set()


@dp.message_handler(state=CreatePost.DESCRIPTION)
async def get_description(message: types.Message, state: FSMContext):
    value = message.text
    if value:
        await update_state(state, new_data=value, key='description', root_key='create_post')
        await message.answer(_('Описание добавлено'))
    await message.answer(_('Добавьте изображение'))
    await CreatePost.IMAGE.set()


@dp.message_handler(state=CreatePost.IMAGE, content_types=types.ContentType.PHOTO)
async def get_photo(message: types.Message, state: FSMContext):
    photos = message.photo
    if not photos:
        await message.edit_text(_('Вы не добавили изображение'))
        return
    image = photos[-1].file_id
    await photos[-1].download()
    file, created = await File.get_or_create(file_id=image,
                                             defaults={'filename': photos[-1].file_id})
    await update_state(state, new_data=file.file_id, key='main_image', root_key='create_post')
    text = _('Подтверждаете?')
    await message.answer(text, reply_markup=await get_create_post_confirm_keyboard())
    await CreatePost.SAVE.set()


@dp.callback_query_handler(ITEM_CB.filter(action='create_confirm'), state=CreatePost.SAVE)
async def get_confirm(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    log.debug(callback_data)
    value = callback_data.get('value')
    if value == 'YES':
        data = await state.get_data()
        post_data = data.get('create_post')
        main_image = await File.get(file_id=post_data.get('main_image'))
        if not main_image.file_path:
            image = await call.bot.get_file(main_image.file_id)
            await image.download()
            main_image.file_path = image.file_path
            await main_image.save()
        with open(main_image.file_path, 'rb') as rb_image:
            post_data['main_image'] = rb_image
            if data.get('post_info'):
                url = f'{REL_URLS["posts"]}{data["post_info"]["pk"]}/'
                resp = await Conn.patch(url, data=post_data, user_id=call.from_user.id)
                if not resp.get('id'):
                    await call.answer(_('Произошла ошибка. Повторите попытке'))
                    if resp.get('Error'):
                        await call.answer(resp.get('Error'))
                else:
                    await call.answer(_('Объявление изменено'), show_alert=True)
                    data.pop('create_post')
                    await state.finish()
                    keyboard, path = await dispatcher('LEVEL_1', user_id=call.from_user.id)
                    data['path'] = path
                    await call.message.answer(_('Возврат на главное меню'), reply_markup=keyboard)
                    await state.update_data(**data)
            else:
                resp, status = await Conn.post(REL_URLS['posts'], data=post_data, user_id=call.from_user.id)
                if status == 201:
                    await call.answer(_('Объявление создано'), show_alert=True)
                    data.pop('create_post')
                    await state.finish()
                    keyboard, path = await dispatcher('LEVEL_1', user_id=call.from_user.id)
                    data['path'] = path
                    await call.message.answer(_('Возврат на главное меню'), reply_markup=keyboard)
                    await state.update_data(**data)
                else:
                    await call.answer(_('Произошла ошибка. Повторите попытке'))
                    if resp.get('Error'):
                        await call.answer(resp.get('Error'))
    else:
        await call.answer(_('Вы можете выбрать нужные этап через меню'))
