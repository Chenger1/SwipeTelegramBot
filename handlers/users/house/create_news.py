import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from loader import dp, Conn

from keyboards.callbacks.user_callback import DETAIL_CB
from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline.create_house import confirm_keyboard, ITEM_CB

from states.state_groups import CreateNewsItem

from middlewares import _

from handlers.users.utils import update_state

from utils.session.url_dispatcher import REL_URLS


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreateNewsItem)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    keys_to_delete = ('create_news',)
    new_dict = {}
    for key, value in data.items():
        if key not in keys_to_delete:
            new_dict[key] = value
    await state.finish()
    new_dict['path'] = path
    await state.update_data(**new_dict)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=CreateNewsItem)
async def go_to_save_news(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if not state_data['create_news'].get('title'):
        await message.answer(_('Вы не ввели заголовок'))
        return
    await message.answer(_('Подтверждаете?\n' +
                           '<b>{title}</b>\n' +
                           '{desc}').format(title=state_data['create_news']['title'],
                                            desc=state_data['create_news'].get('text', '')),
                         reply_markup=confirm_keyboard)
    await CreateNewsItem.SAVE.set()


@dp.message_handler(Text(equals=['Перейти к заголовку', 'Go to title']), state=CreateNewsItem)
async def go_to_news_title(message: types.Message):
    await message.answer(_('Введите заголовок'))
    await CreateNewsItem.TITLE.set()


@dp.message_handler(Text(equals=['Перейти к тексту', 'Go to text']), state=CreateNewsItem)
async def go_to_news_title(message: types.Message):
    await message.answer(_('Введите текст'))
    await CreateNewsItem.TEXT.set()


@dp.callback_query_handler(DETAIL_CB.filter(action='add_news'))
async def add_news(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await CreateNewsItem.STARTER.set()
    house_pk = callback_data.get('pk')
    keyboard, path = await dispatcher('LEVEL_4_ADD_NEWS', call.from_user.id)
    logging.info({'path': path})
    await update_state(state, house_pk, 'house', 'create_news')
    await call.message.answer(_('Введите заголовок'), reply_markup=keyboard)
    await CreateNewsItem.TITLE.set()
    await call.answer()


@dp.message_handler(state=CreateNewsItem.TITLE)
async def add_news_title(message: types.Message, state: FSMContext):
    answer = message.text
    if not answer:
        await message.answer(_('Заголовок не может быть пустым'))
        return
    await update_state(state, answer, 'title', 'create_news')
    await message.answer(_('Добавьте текст новости'))
    await CreateNewsItem.TEXT.set()


@dp.message_handler(state=CreateNewsItem.TEXT)
async def add_news_text(message: types.Message, state: FSMContext):
    await update_state(state, message.text, 'text', 'create_news')
    state_data = await state.get_data()
    await message.answer(_('Подтверждаете?\n' +
                           '<b>{title}</b>\n' +
                           '{desc}').format(title=state_data['create_news']['title'],
                                            desc=state_data['create_news']['text']),
                         reply_markup=confirm_keyboard)
    await CreateNewsItem.SAVE.set()


@dp.callback_query_handler(ITEM_CB.filter(action='create_confirm'), state=CreateNewsItem.SAVE)
async def save_news(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    if value:
        state_data = await state.get_data()
        news_data = state_data.get('create_news')
        resp, status = await Conn.post(REL_URLS['news'], data=news_data, user_id=call.from_user.id)
        if status == 201:
            await call.answer(_('Новость добавлена'), show_alert=True)
        else:
            await call.answer(_('Произошла ошибка'), show_alert=True)
            for key, value in resp.items():
                logging.info(f'{key} - {value}')
    else:
        await call.answer(_('Вы можете выбрать этап через меню'))
