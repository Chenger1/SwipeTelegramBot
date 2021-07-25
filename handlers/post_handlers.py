from aiogram import types

import logging

from main import dp, session_manager, post_agent, bot

from utils.url_dispatcher import REL_URLS
from utils import keyboards


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='like_post'))
async def process_like_post(callback_query: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = REL_URLS['like_dislike'].format(pk=pk)
    data = {'action': 'like'}
    resp = await session_manager.patch(url, data=data, user_id=callback_query.from_user.id)
    if resp.get('post'):
        await bot.send_message(callback_query.from_user.id, text='Лайк поставлен')
        url = f'{REL_URLS["posts_public"]}{pk}/'
        resp = await session_manager.get(url, user_id=callback_query.from_user.id)
        data = await post_agent.one_iteration(resp)
        keyboard = keyboards.get_post_detail_keyboard(post_pk=pk, flat_pk=resp['flat_info']['id'])
        await bot.send_message(callback_query.from_user.id, 'Подробнее об объявлении')
        await bot.send_message(callback_query.from_user.id, text=data.data, parse_mode=types.ParseMode.MARKDOWN,
                               reply_markup=keyboard)
    else:
        await bot.send_message(callback_query.from_user.id, 'Произошла ошибка')


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='dislike_post'))
async def process_dislike_post(callback_query: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = REL_URLS['like_dislike'].format(pk=pk)
    data = {'action': 'dislike'}
    resp = await session_manager.patch(url, data=data, user_id=callback_query.from_user.id)
    if resp.get('post'):
        await bot.send_message(callback_query.from_user.id, text='Дизлайк поставлен')
        url = f'{REL_URLS["posts_public"]}{pk}/'
        resp = await session_manager.get(url, user_id=callback_query.from_user.id)
        data = await post_agent.one_iteration(resp)
        keyboard = keyboards.get_post_detail_keyboard(post_pk=pk, flat_pk=resp['flat_info']['id'])
        await bot.send_message(callback_query.from_user.id, 'Подробнее об объявлении')
        await bot.send_message(callback_query.from_user.id, text=data.data, parse_mode=types.ParseMode.MARKDOWN,
                               reply_markup=keyboard)
    else:
        await bot.send_message(callback_query.from_user.id, 'Произошла ошибка')
