import aiohttp

from aiogram import types

from main import dp

from utils import prepare_url


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!. I`m Swipe Bot')


@dp.message_handler()
async def echo(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(prepare_url('main/posts_public/')) as resp:
            await message.reply(f'Status: {resp.status}. Data: {await resp.json()}')
