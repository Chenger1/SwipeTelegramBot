from aiogram import types
from aiogram.utils.exceptions import MessageNotModified, MessageTextIsEmpty

from typing import Optional, Iterable, Union, Callable, Coroutine

from utils.session.url_dispatcher import REL_URLS
from utils.helpers import get_page

from deserializers.base import BaseDeserializer

from loader import Conn

from middlewares import _


async def prepare_dict(obj: Optional[dict]) -> Optional[dict]:
    if obj:
        new_dict = {}
        for key, value in obj.items():
            if type(value) in (int, str) and key != 'path':
                new_dict[key] = value
        return new_dict


async def get_list(user_id: str, key: str, page: str, params: dict = None,
                   data: dict = None) -> dict:
    url = f'{REL_URLS[key]}?page={page}'
    resp = await Conn.get(url, user_id=user_id, params=params,
                          data=data)
    return resp


async def prepare_text(data: Iterable) -> Optional[str]:
    if data:
        text = ''
        for index, item in enumerate(data, start=1):
            text += f'{index}. {item.data}\n'
        return text


async def send_answer(message: Union[types.Message, types.CallbackQuery],
                      text: str, new_callback_answer: bool,
                      keyboard_cor: Coroutine = None):
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=await keyboard_cor)

    if isinstance(message, types.CallbackQuery):
        if new_callback_answer:
            await message.message.answer(text, reply_markup=await keyboard_cor)
            await message.answer()
        else:
            try:
                await message.message.edit_text(text, reply_markup=await keyboard_cor)
                await message.answer()
            except (MessageTextIsEmpty, MessageNotModified):
                await message.answer(text=_('Больше ничего нет'), show_alert=True)


async def handle_list(message: Union[types.Message, types.CallbackQuery],
                      key: str, page: str, deserializer: BaseDeserializer,
                      keyboard: Callable, detail_action: str, list_action: str,
                      params: dict = None, data: dict = None,
                      new_callback_answer: bool = False):
    resp = await get_list(message.from_user.id, key, page,
                          await prepare_dict(params), await prepare_dict(data))
    items_data = await deserializer.make_list(resp)
    text = await prepare_text(items_data)
    if text:
        pages = {
            'next': await get_page(resp.get('next')) or 'last',
            'prev': await get_page(resp.get('previous')) or '1',
            'first': '1',
            'current': page
        }
        keyboard_cor = keyboard(items_data, pages, key, detail_action, list_action)
        await send_answer(message, text, new_callback_answer, keyboard_cor)
    else:
        await send_answer(message, _('Ничего нет'), new_callback_answer)
