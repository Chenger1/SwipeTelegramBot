import logging
import os
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from keyboards.inline import create_house
from loader import dp, Conn

from keyboards.callbacks.user_callback import DETAIL_CB
from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline.create_house import confirm_keyboard, ITEM_CB

from states.state_groups import CreateDocument

from middlewares import _

from handlers.users.utils import update_state
from utils.db_api.models import File

from utils.session.url_dispatcher import REL_URLS


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreateDocument)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    keys_to_delete = ('create_doc', 'house_pk')
    new_dict = {}
    for key, value in data.items():
        if key not in keys_to_delete:
            new_dict[key] = value
    await state.finish()
    new_dict['path'] = path
    await state.update_data(**new_dict)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=CreateDocument)
async def go_to_save_doc(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    doc_data = state_data.get('create_doc')
    keys = ('house', 'name', 'file')
    if all(key in doc_data for key in keys):
        await message.answer(_('Подтверждаете?\n' +
                               '<b>{title}</b>\n' +
                               '{desc}').format(title=state_data['create_news']['title'],
                                                desc=state_data['create_news'].get('text', '')),
                             reply_markup=confirm_keyboard)
        await CreateDocument.SAVE.set()
    else:
        text = _('Вы не указали: \n')
        if not doc_data.get('name'):
            text += _('Название\n')
        if not doc_data.get('file'):
            text += _('Файл\n')
        await message.answer(text)


@dp.message_handler(Text(equals=['Перейти к названию', 'Go to name']), state=CreateDocument)
async def go_to_doc_name(message: types.Message):
    await message.answer(_('Введите название документа'))
    await CreateDocument.NAME.set()


@dp.message_handler(Text(equals=['Перейти к файлу', 'Go to file']), state=CreateDocument)
async def go_to_doc_file(message: types.Message):
    await message.answer(_('Добавьте файл'))
    await CreateDocument.FILE.set()


@dp.callback_query_handler(DETAIL_CB.filter(action='add_doc'))
async def add_doc(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await CreateDocument.STARTER.set()
    house_pk = callback_data.get('pk')
    keyboard, path = await dispatcher('LEVEL_4_ADD_DOC', call.from_user.id)
    logging.info({'path': path})
    await update_state(state, house_pk, 'house', 'create_doc')
    await call.message.answer(_('Введите название файла'), reply_markup=keyboard)
    await CreateDocument.NAME.set()
    await call.answer()


@dp.message_handler(state=CreateDocument.NAME)
async def add_doc_name(message: types.Message, state: FSMContext):
    answer = message.text
    if not answer:
        await message.answer(_('Название не может быть пустым'))
        return
    await update_state(state, answer, 'name', 'create_doc')
    await message.answer(_('Добавьте файл'))
    await CreateDocument.FILE.set()


async def prepare_file_to_send(file, house_pk: int):
    await file.download()
    filename = os.path.split(file.file_path)[-1]
    file, created = await File.get_or_create(file_id=file.file_id,
                                             defaults={'filename': filename,
                                                       'file_path': file.file_path,
                                                       'parent_id': house_pk})
    return file


@dp.message_handler(state=CreateDocument.FILE, content_types=types.ContentTypes.PHOTO)
async def add_doc_photo(message: types.Message, state: FSMContext):
    photos = message.photo
    image_id = photos[-1].file_id
    image = await message.bot.get_file(image_id)
    data = await state.get_data()
    file = await prepare_file_to_send(image, data['create_doc']['house'])
    await update_state(state, file.file_id, 'file', 'create_doc')
    text = _('Подтверждаете?')
    await message.answer(text, reply_markup=create_house.confirm_keyboard)
    await CreateDocument.SAVE.set()


@dp.message_handler(state=CreateDocument.FILE, content_types=types.ContentTypes.DOCUMENT)
async def add_doc_file(message: types.Message, state: FSMContext):
    doc_id = message.document.file_id
    doc = await message.bot.get_file(doc_id)
    data = await state.get_data()
    file = await prepare_file_to_send(doc, data['create_doc']['house'])
    await update_state(state, file.file_id, 'file', 'create_doc')
    text = _('Подтверждаете?')
    await message.answer(text, reply_markup=create_house.confirm_keyboard)
    await CreateDocument.SAVE.set()


@dp.callback_query_handler(ITEM_CB.filter(action='create_confirm'), state=CreateDocument.SAVE)
async def save_news(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    if value:
        state_data = await state.get_data()
        doc_data = state_data.get('create_doc')
        file = await File.get(file_id=doc_data.get('file'), parent_id=doc_data.get('house'))
        if not file.file_path:
            telegram_file = await call.bot.get_file(file.file_id)
            await telegram_file.download()
            file.file_path = telegram_file.file_path
            await file.save()
        with open(file.file_path, 'rb') as rb_file:
            doc_data['file'] = rb_file
            resp, status = await Conn.post(REL_URLS['documents'], data=doc_data, user_id=call.from_user.id)
            if status == 201:
                await call.answer(_('Документ добавлен'), show_alert=True)
                state_data.pop('create_doc')
                state_data.pop('house_pk')
                await state.finish()
                await state.update_data(**state_data)
            else:
                await call.answer(_('Произошла ошибка. Попробуйте ещё раз'))
                for key, value in resp.items():
                    logging.info(f'{key} - {value}')
    else:
        await call.answer(_('Вы можете выбрать этап через меню'))
