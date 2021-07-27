from aiogram import types
import asyncio

import logging

from main import dp, session_manager, post_agent, bot, favorite_post_agent

from utils.url_dispatcher import REL_URLS
from utils import keyboards
from utils import helper


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='like_post'))
async def process_like_post(callback_query: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = REL_URLS['like_dislike'].format(pk=pk)
    data = {'action': 'like'}
    resp = await session_manager.patch(url, data=data, user_id=callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, text='Лайк поставлен')

    # Get post again
    url = f'{REL_URLS["posts_public"]}{pk}/'
    resp = await session_manager.get(url, user_id=callback_query.from_user.id)
    data = await post_agent.one_iteration(resp)
    if resp.get('main_image'):
        await helper.process_getting_file(resp.get('main_image'), callback_query.from_user.id)
    keyboard = await keyboards.get_post_detail_keyboard(post_pk=pk, flat_pk=resp['flat_info']['id'])
    await bot.send_message(callback_query.from_user.id, 'Подробнее об объявлении')
    await bot.send_message(callback_query.from_user.id, text=data.data, parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=keyboard)


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='dislike_post'))
async def process_dislike_post(callback_query: types.CallbackQuery, callback_data: dict):
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = REL_URLS['like_dislike'].format(pk=pk)
    data = {'action': 'dislike'}
    resp = await session_manager.patch(url, data=data, user_id=callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, text='Дизлайк поставлен')

    # Get post again
    url = f'{REL_URLS["posts_public"]}{pk}/'
    resp = await session_manager.get(url, user_id=callback_query.from_user.id)
    data = await post_agent.one_iteration(resp)
    if resp.get('main_image'):
        await helper.process_getting_file(resp.get('main_image'), callback_query.from_user.id)
    keyboard = await keyboards.get_post_detail_keyboard(post_pk=pk, flat_pk=resp['flat_info']['id'])
    await bot.send_message(callback_query.from_user.id, 'Подробнее об объявлении')
    await bot.send_message(callback_query.from_user.id, text=data.data, parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=keyboard)


@dp.callback_query_handler(keyboards.COMPLAINT_CB.filter(action='complaint'))
async def process_complaint(callback_query: types.CallbackQuery, callback_data: dict):
    """
        If callback_data contains - 'type' key - uses this type to create new complaint.
        Otherwise, create inline keyboard with complaint types for user.
    """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    if callback_data.get('type') != '_':
        resp, status = await session_manager.post(REL_URLS['complaint'],
                                                  data={'post': pk, 'type': callback_data.get('type')},
                                                  user_id=callback_query.from_user.id)
        if status == 201:
            await bot.send_message(callback_query.from_user.id,
                                   'Жалоба отправлена. Модератор в скором времени рассмотрит её')
        elif status == 409:
            await bot.send_message(callback_query.from_user.id,
                                   'Вы уже отправили жалобу. Она на рассмотрении')
        else:
            logging.error(resp)
            await bot.send_message(callback_query.from_user.id,
                                   'Произошла ошибка. Повторите попытку')
    else:
        keyboard = await keyboards.get_post_complaint_types(post_pk=pk)
        await bot.send_message(callback_query.from_user.id, 'Укажите причину жалобы', reply_markup=keyboard)


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='save_to_favorites'))
async def process_saving_to_favorites(callback_query: types.CallbackQuery, callback_data: dict):
    """ Save post in user`s favorite """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    resp, status = await session_manager.post(REL_URLS['favorites'], data={'post': pk},
                                              user_id=callback_query.from_user.id)
    if status == 201:
        await bot.send_message(callback_query.from_user.id,
                               'Объявление добавлено в список избранного')
    elif status == 409:
        await bot.send_message(callback_query.from_user.id,
                               'Это объявление уже в вашем списке избранного')
    else:
        logging.error(resp)
        await bot.send_message(callback_query.from_user.id,
                               'Произошла ошибка. Попробуйте ещё раз')


@dp.message_handler(commands=['favorites'])
async def favorites_message_handler(message: types.Message):
    """ List user`s favorites list """
    resp = await session_manager.get(REL_URLS['favorites'], user_id=message.from_user.id)
    if not resp:
        await message.reply(text='Нет сохраненных объявлений')
    else:
        # resp = [elem['post'] for elem in resp]
        data = await favorite_post_agent.objects_repr(resp)
        coros = []
        for item in data:
            keyboard = await keyboards.get_detail_keyboard(item[1], 'Удалить из избранного', 'delete_from_favorites')
            coros.append(message.reply(text=item[0].data, reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN))
        await asyncio.gather(*coros)


@dp.callback_query_handler(keyboards.DETAIL_CB.filter(action='delete_from_favorites'))
async def process_delete_from_favorites(callback_query: types.CallbackQuery, callback_data: dict):
    """ Delete given post from user`s favorites list """
    logging.info(callback_data)
    pk = callback_data['pk']
    await bot.answer_callback_query(callback_query.id)
    url = f'{REL_URLS["favorites"]}{pk}/'
    resp, status = await session_manager.delete(url, callback_query.from_user.id)
    if status == 204:
        await bot.send_message(callback_query.from_user.id, 'Запись удалена')
    else:
        logging.error(resp)
        await bot.send_message(callback_query.from_user.id, 'Произошла ошибка. Попробуйте снова')
