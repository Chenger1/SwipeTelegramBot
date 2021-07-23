from aiogram import types

import asyncio
import logging

from main import dp, session_manager, post_agent, bot

from utils.url_dispatcher import REL_URLS
from utils.keyboards import get_detail_keyboard, DETAIL_CB


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!. I`m Swipe Bot. Choose command in menu to get info.')


@dp.callback_query_handler(DETAIL_CB.filter(action='detail'))
async def process_callback_post(callback_query: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'pk {pk}')


@dp.message_handler(commands=['public_posts'])
async def public_posts(message: types.Message):
    """ This public apis don`t require  auth tokens """
    resp = await session_manager.get(REL_URLS['posts_public'])
    data = await post_agent.posts_repr(resp)
    coros = []
    for item in data:
        keyboard = get_detail_keyboard(item.pk, 'Подробнее о публикации')
        coros.append(message.answer(item.data,
                                    reply_markup=keyboard))
    await asyncio.gather(*coros)
