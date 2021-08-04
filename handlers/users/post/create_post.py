import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from states.state_groups import CreatePost
from deserializers.post import HouseForCreatePost, BaseDeserializer, FlatForCreatePost

from middlewares import _

from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline.create_post import (ITEM_CB, get_item_for_create_post, get_payment_options,
                                          get_communication_keyboard, get_create_post_confirm_keyboard)
from keyboards.callbacks.user_callback import DETAIL_CB

from utils.session.url_dispatcher import REL_URLS
from utils.db_api.models import File

from typing import Union


house_des = HouseForCreatePost()
flat_des = FlatForCreatePost()


async def list_items(user_id: int, url: str, deserializer: BaseDeserializer,
                     keyboard, error_text: str, action: str):
    resp = await Conn.get(url, user_id=user_id)
    if resp:
        data = await deserializer.make_list(resp)
        text = ''
        for index, item in enumerate(data, start=1):
            text += f'{index}. {item.data}\n'
        return text, keyboard(data, action), True
    else:
        return error_text, keyboard([]), False


async def update_state(state: FSMContext, new_data: Union[int, str, dict],
                       key: str):
    data = await state.get_data()
    post_data = data.get('create_post')
    post_data[key] = new_data
    await state.update_data(create_post=post_data)


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreatePost)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    if data.get('create_post'):
        data.pop('create_post')
    await state.finish()
    data['path'] = path
    await state.update_data(**data)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=CreatePost)
async def save_post_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get('create_post')
    keys = ('house', 'flat', 'payment_options', 'communication',
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
        if not post_data.get('communication'):
            text += _('Способ коммуникации с вами\n')
        if not post_data.get('description'):
            text += _('Описание\n')
        if not post_data.get('main_image'):
            text += _('Фото к объявлению\n')
        await message.answer(text)


@dp.message_handler(Text(equals=['Перейти к дому', 'Go to house']), state=CreatePost)
async def go_to_house(message: types.Message):
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


@dp.message_handler(Text(equals=['Перейти к квартире', 'Go to flat']), state=CreatePost)
async def go_to_flat(message: types.Message):
    error_text = _('Квартир нет. Добавьте квартиру, преждем чем создавать объявление')
    text, keyboard_cor, status = await list_items(user_id=message.from_user.id,
                                                  url=REL_URLS['flats'],
                                                  deserializer=flat_des,
                                                  keyboard=get_item_for_create_post,
                                                  error_text=error_text,
                                                  action='add_flat')
    if not status:
        await message.answer(text)
        keyboard_cor.close()
        return
    await message.answer(_('Выберите квартиру'))
    await message.answer(text, reply_markup=await keyboard_cor)
    await CreatePost.FLAT.set()


@dp.message_handler(Text(equals=['Перейти к цене', 'Go to price']), state=CreatePost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get('create_post')
    await message.answer(_('Текущая цена: {price}\n' +
                           'Введите новую цену').format(price=post_data.get('price', _('Не указано'))))
    await CreatePost.PRICE.set()


@dp.message_handler(Text(equals=['Перейти к способу платежа', 'Go to payment options']), state=CreatePost)
async def go_to_payment_option(message: types.Message):
    await message.answer(_('Выберите метод оплаты'),
                         reply_markup=await get_payment_options())
    await CreatePost.PAYMENT.set()


@dp.message_handler(Text(equals=['Перейти к вариантам связи', 'Go to communication']), state=CreatePost)
async def go_to_communications(message: types.Message):
    await message.answer(_('Выберите метод коммуникации'), reply_markup=await get_communication_keyboard())
    await CreatePost.COMMUNICATION.set()


@dp.message_handler(Text(equals=['Перейти к описанию', 'Go to description']), state=CreatePost)
async def go_to_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get('create_post')
    if post_data:
        current_desc = post_data.get('description', _('Не указано'))
        await message.answer(_('Текущее описание\n {desc}').format(desc=current_desc))
    await message.answer('Добавьте описание')
    await CreatePost.DESCRIPTION.set()


@dp.message_handler(Text(equals=['Перейти к фото', 'Go to photo']), state=CreatePost)
async def go_to_photo(message: types.Message):
    await message.answer(_('Добавьте изображение'))
    await CreatePost.IMAGE.set()


@dp.message_handler(Text(equals=['Добавить новую публикацию', 'Add new post']))
async def add_post(message: types.Message, state: FSMContext):
    await CreatePost.STARTER.set()
    keyboard, path = await dispatcher('LEVEL_3_CREATE_POST', message.from_user.id)
    await message.answer(_('Заполните форму для фитрации'),
                         reply_markup=keyboard)
    await state.update_data(path=path)
    logging.info({'path': path})
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
    logging.info(callback_data)
    pk = callback_data.get('pk')
    url = f'{REL_URLS["houses"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    if resp:
        data = await house_des.for_detail(resp)
        text = _('Выбранный дом:\n' +
                 data.data)
        await call.message.answer(text)
        await update_state(state, new_data=pk, key='house')
        await call.answer()

        error_text = _('Квартир нет. Добавьте квартиру, преждем чем создавать объявление')
        text, keyboard_cor, status = await list_items(user_id=call.from_user.id,
                                                      url=REL_URLS['flats'],
                                                      deserializer=flat_des,
                                                      keyboard=get_item_for_create_post,
                                                      error_text=error_text,
                                                      action='add_flat')
        if not status:
            await call.message.answer(text)
            keyboard_cor.close()
            return
        await call.message.answer(_('Выберите квартиру'))
        await call.message.answer(text, reply_markup=await keyboard_cor)
        await CreatePost.FLAT.set()
    else:
        await call.answer(_('Такого дома нет в системе. Выберите другой'))


@dp.callback_query_handler(DETAIL_CB.filter(action='add_flat'), state=CreatePost.FLAT)
async def get_flat(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    pk = callback_data.get('pk')
    url = f'{REL_URLS["flats"]}{pk}/'
    resp = await Conn.get(url, user_id=call.from_user.id)
    if resp:
        data = await flat_des.for_detail(resp)
        text = _('Выбранная квартира:\n' +
                 data.data)
        await call.message.answer(text)
        await update_state(state, new_data=pk, key='flat')
        await call.answer()

        await call.message.answer(_('Выберите метод оплаты'), reply_markup=await get_payment_options())
        await CreatePost.PAYMENT.set()
    else:
        await call.answer(_('Нет такой квартиры в системе. Выберите другую'))


@dp.callback_query_handler(ITEM_CB.filter(action='add_payment'), state=CreatePost.PAYMENT)
async def get_payment(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    await update_state(state, new_data=value, key='payment_options')
    await call.answer(_('Метод оплаты добавлен'))
    await call.message.answer(_('Введите цену'))
    await CreatePost.PRICE.set()


@dp.message_handler(state=CreatePost.PRICE)
async def get_price(message: types.Message, state: FSMContext):
    value = message.text
    try:
        value = value.replace(' ', '')
        await update_state(state, new_data=value, key='price')
        await message.answer(_('Цена добавлена'))
        await message.answer(_('Выберите метод коммуникации'), reply_markup=await get_communication_keyboard())
        await CreatePost.COMMUNICATION.set()
    except ValueError:
        await message.answer(_('Неправильный формат ввода'))


@dp.callback_query_handler(ITEM_CB.filter(action='add_comm'), state=CreatePost.COMMUNICATION)
async def get_communication(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    await update_state(state, new_data=value, key='communication')
    await call.answer(_('Способ связи добавлен'))
    await call.message.answer('Добавьте описание')
    await CreatePost.DESCRIPTION.set()


@dp.message_handler(state=CreatePost.DESCRIPTION)
async def get_description(message: types.Message, state: FSMContext):
    value = message.text
    if value:
        await update_state(state, new_data=value, key='description')
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
    await update_state(state, new_data=file.file_id, key='main_image')
    text = _('Подтверждаете?')
    await message.answer(text, reply_markup=await get_create_post_confirm_keyboard())
    await CreatePost.SAVE.set()


@dp.callback_query_handler(ITEM_CB.filter(action='create_confirm'), state=CreatePost.SAVE)
async def get_confirm(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    if value == 'YES':
        data = await state.get_data()
        post_data = data.get('create_post')
        main_image = await File.get(file_id=post_data.get('main_image'))
        image = await call.bot.get_file(main_image.file_id)
        with open(image.file_path, 'rb') as rb_image:
            post_data['main_image'] = rb_image
            resp, status = await Conn.post(REL_URLS['posts'], data=post_data, user_id=call.from_user.id)
        if status == 201:
            await call.answer(_('Объявление создано'), show_alert=True)
            data.pop('create_post')
            await state.finish()
            await state.update_data(data)
        else:
            await call.answer(_('Произошла ошибка. Повторите попытке'))
            if resp.get('Error'):
                await call.answer(resp.get('Error'))
    else:
        await call.answer(_('Вы можете выбрать нужные этап через меню'))
