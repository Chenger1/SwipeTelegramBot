from aiogram import types
from aiogram.dispatcher.filters.builtin import Text

from keyboards.inline import create_house
from keyboards.inline.user_keyboards import get_keyboard_for_list
from loader import dp, Conn

from utils.session.url_dispatcher import REL_URLS

from handlers.users.utils import handle_list

from deserializers.house import RequestDeserializer


from middlewares import _


request_des = RequestDeserializer()


@dp.message_handler(Text(equals=['Входящие запросы на добавление в шахматку', 'Income request to chest']))
async def requests_to_chest(message: types.Message):
    await handle_list(message, key='requests', page='1', deserializer=request_des,
                      keyboard=get_keyboard_for_list, detail_action='request_detail',
                      list_action='request_list')
