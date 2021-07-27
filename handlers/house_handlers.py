from aiogram import types
import asyncio

import logging

from main import dp, session_manager, bot, news_agent

from utils.url_dispatcher import REL_URLS
from utils import keyboards
from utils import helper


@dp.callback_query_handler(keyboards.LIST_CB.filter(action='news_list'))
async def process_news_list(callback_query: types.CallbackQuery, callback_data: dict):
    """ Get house`s pk and list all it`s news """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    resp = await session_manager.get(REL_URLS['news'], params={'house': pk}, user_id=callback_query.from_user.id)
    if resp:
        data = await news_agent.objects_repr(resp)
        coros = []
        for item in data:
            coros.append(bot.send_message(callback_query.from_user.id, text=item.data,
                                          parse_mode=types.ParseMode.MARKDOWN))
        await asyncio.gather(*coros)
    else:
        await bot.send_message(callback_query.from_user.id, text='Новостей пока нет')


@dp.callback_query_handler(keyboards.LIST_CB.filter(action='documents_list'))
async def process_documents_list(callback_query: types.CallbackQuery, callback_data: dict):
    """
     Get list of all documents in house. And retrieve them one by one
     """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    resp = await session_manager.get(REL_URLS['documents'], params={'house': pk}, user_id=callback_query.from_user.id)
    if resp:
        for doc in resp:
            await helper.process_getting_file(doc.get('file'), callback_query.from_user.id)
    else:
        await bot.send_message(callback_query.from_user.id, text='Документов нет')
