from aiogram import types

import asyncio

from main import dp, session_manager, post_agent

from utils.url_dispatcher import REL_URLS


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!. I`m Swipe Bot. Choose command in menu to get info.')


@dp.message_handler(commands=['public_posts'])
async def public_posts(message: types.Message):
    """ This public apis don`t require  auth tokens """
    resp = await session_manager.get(REL_URLS['posts_public'])
    data = await post_agent.posts_repr(resp)
    coros = [message.reply(item) for item in data]
    await asyncio.gather(*coros)
