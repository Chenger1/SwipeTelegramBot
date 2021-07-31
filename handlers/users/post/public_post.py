import asyncio

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text

from loader import dp, Conn
from utils.session.url_dispatcher import REL_URLS
from deserializers.post import PostDeserializer


post_des = PostDeserializer()


@dp.message_handler(Text(equals=['Список публикаций', 'List ads']))
async def public_post(message: types.Message):
    """ List of all posts """
    resp = await Conn.get(REL_URLS['posts_public'],
                          user_id=message.from_user.id)
    if resp:
        data = await post_des.make_list(resp)
        coros = []
        await message.answer(text='Список публикаций')
        for item in data:
            coros.append(message.answer(text=item.data))
        await asyncio.gather(*coros)
    else:
        await message.answer(text='Публикаций нет')
