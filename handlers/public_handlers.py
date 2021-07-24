from aiogram import types

import asyncio
import logging

from main import dp, session_manager, post_agent, house_agent, flat_agent, bot

from utils.url_dispatcher import REL_URLS
from utils import keyboards


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!. I`m Swipe Bot. Choose command in menu to get info.')


# POSTS


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='post_detail'))
async def process_callback_post(callback_query: types.CallbackQuery, callback_data: dict):
    """
        Get detail info about post object
    """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = f'{REL_URLS["posts_public"]}{pk}/'
    resp = await session_manager.get(url)
    data = await post_agent.one_iteration(resp)
    keyboard = keyboards.get_detail_keyboard(resp['flat_info']['id'], 'Подробнее о квартире', action='flat_detail')
    await bot.send_message(callback_query.from_user.id, 'Подробнее об объявлении')
    await bot.send_message(callback_query.from_user.id, text=data.data, parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=keyboard)


@dp.message_handler(commands=['public_posts'])
async def public_posts(message: types.Message):
    """ This public apis don`t require  auth tokens """
    resp = await session_manager.get(REL_URLS['posts_public'])
    data = await post_agent.objects_repr(resp)
    coros = []
    for item in data:
        keyboard = keyboards.get_detail_keyboard(item.pk, 'Подробнее о публикации', action='post_detail')
        coros.append(message.answer(text=item.data,
                                    reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN))
    await asyncio.gather(*coros)


# HOUSES
@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='house_detail'))
async def process_callback_house(callback_query: types.CallbackQuery, callback_data: dict):
    """ Gets detail info about house object """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = f'{REL_URLS["houses_public"]}{pk}/'
    resp = await session_manager.get(url)
    data = await house_agent.one_iteration(resp)
    await bot.send_message(callback_query.from_user.id, 'Подробнее о доме')
    await bot.send_message(callback_query.from_user.id, text=data.data, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['public_houses'])
async def public_houses(message: types.Message):
    """ This public apis don`t require auth token """
    resp = await session_manager.get(REL_URLS['houses_public'])
    data = await house_agent.objects_repr(resp)
    coros = []
    for item in data:
        keyboard = keyboards.get_house_keyboard(item.pk)
        coros.append(message.reply(text=item.data, reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN))
    await asyncio.gather(*coros)


# FLATS
@dp.callback_query_handler(keyboards.LIST_CB.filter(action='house_flats_list'))
async def process_callback_flats_list_by_house(callback_query: types.CallbackQuery, callback_data: dict):
    """ Gets list of all flats for given house """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = f'{REL_URLS["flats_public"]}'
    params = {'house__pk': pk}
    resp = await session_manager.get(url, params=params)
    data = await flat_agent.objects_repr(resp)
    coros = []
    await bot.send_message(callback_query.from_user.id, 'Список квартир в доме')
    for item in data:
        keyboard = keyboards.get_detail_keyboard(item.pk, 'Подробнее о квартире', action='flat_detail')
        coros.append(bot.send_message(callback_query.from_user.id,
                                      text=item.data, reply_markup=keyboard,
                                      parse_mode=types.ParseMode.MARKDOWN))
    await asyncio.gather(*coros)


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='flat_detail'))
async def process_callback_flat_detail(callback_query: types.CallbackQuery, callback_data: dict):
    """ Gets detail info about flat """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = f'{REL_URLS["flats_public"]}{pk}'
    resp = await session_manager.get(url)
    data = await flat_agent.one_iteration(resp)
    await bot.send_message(callback_query.from_user.id, text=data.data, parse_mode=types.ParseMode.MARKDOWN)
