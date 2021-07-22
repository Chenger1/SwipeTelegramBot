from aiogram import types

from main import dp, session_manager


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!. I`m Swipe Bot')


@dp.message_handler()
async def echo(message: types.Message):
    status, resp = await session_manager.get('main/posts_public/')
    await message.reply(f'Status: {status}. Data: {resp}')
