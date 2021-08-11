from aiogram import types
from aiogram.utils.exceptions import MessageNotModified, MessageTextIsEmpty
from aiogram.dispatcher import FSMContext

from typing import Optional, Iterable, Union, Callable, Coroutine

from utils.db_api.models import File
from utils.session.url_dispatcher import REL_URLS
from utils.helpers import get_page

from deserializers.base import BaseDeserializer

from loader import Conn, log

from middlewares import _


async def prepare_dict(obj: Optional[dict]) -> Optional[dict]:
    """
    Data and Query params for http request are got from FSMContext. And might contain an extra keys,
    such as keyboard 'path', etc. Also, there can be object - dicts, lists
    This function returns new dict with only - integers and strings as value for keys
    :param obj: state from FSMContext in general
    :return: new dict
    """
    if obj:
        new_dict = {}
        for key, value in obj.items():
            if type(value) in (int, str) and key != 'path':
                new_dict[key] = value
        return new_dict


async def get_list(user_id: str, key: str, page: str, params: dict = None,
                   data: dict = None, custom_url: str = None) -> dict:
    """
    Makes request and returns response
    :param custom_url: f'{REL_URLS[key]}?house__pk=1&page={page}' for example
    :param user_id: user_id in telegram.
    :param key: REL_URLS contains all http paths in dict. Key for get path
    :param page: For pagination
    :param params: Additional parameters for request
    :param data: Additional parameters for request
    :return: Response
    """
    url = custom_url or f'{REL_URLS[key]}?page={page}'
    resp = await Conn.get(url, user_id=user_id, params=params,
                          data=data)
    return resp


async def prepare_text(data: Iterable) -> Optional[str]:
    """
    Using deserialized info from response, we have to prepare it to send to user.
    Using this data, we make list from 1, to {n} elements
    """
    if data:
        text = ''
        for index, item in enumerate(data, start=1):
            text += f'{index}. {item.data}\n'
        return text


async def send_answer(message: Union[types.Message, types.CallbackQuery],
                      text: str, new_callback_answer: bool,
                      keyboard_cor: Coroutine = None):
    """
    In depends on message type, this function "send" answer as a new message or edit current.
    """
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=await keyboard_cor)

    elif isinstance(message, types.CallbackQuery):
        if new_callback_answer:
            await message.message.answer(text, reply_markup=await keyboard_cor)
            await message.answer()
        else:
            try:
                await message.message.edit_text(text, reply_markup=await keyboard_cor)
                await message.answer()
            except (MessageTextIsEmpty, MessageNotModified):
                await message.answer(text=_('Больше ничего нет'), show_alert=True)
    else:
        keyboard_cor.close()


async def handle_list(message: Union[types.Message, types.CallbackQuery],
                      key: str, page: str, deserializer: BaseDeserializer,
                      keyboard: Callable, detail_action: str, list_action: str,
                      params: dict = None, data: dict = None,
                      new_callback_answer: bool = False,
                      custom_url: str = None, pk: int = None):
    """
    1) Gets response(with list of items) from API
    2) Pass response to deserializer class. Gets tuple with list of namedtuple.
    Every namedtuple contains ['id'] of object and ['data'] - object description, text
    3) Combine independent text into one message
    4) If 'text' variable is EMPTY:
        Send common 'answer' - 'There is nothing to show'
       If 'text' variable is NOT empty:
            Prepare 'page' dict - it will be used to manage pages
            5) Prepare keyboard for message
    """
    resp = await get_list(message.from_user.id, key, page,
                          await prepare_dict(params), await prepare_dict(data),
                          custom_url)  # 1)
    items_data = await deserializer.make_list(resp)  # 2)
    text = await prepare_text(items_data)  # 3)
    pages = {
        'next': await get_page(resp.get('next')) or 'last',
        'prev': await get_page(resp.get('previous')) or '1',
        'first': '1',
        'current': page
    }
    keyboard_cor = keyboard(items_data, pages, key, detail_action, list_action, pk=pk)
    if text:
        await send_answer(message, text, new_callback_answer, keyboard_cor)
    else:
        await send_answer(message, _('Ничего нет'), new_callback_answer, keyboard_cor)


async def send_with_image(call: types.CallbackQuery, resp: dict, pk: int,
                          text: str, keyboard: types.InlineKeyboardMarkup,
                          image_key: str):
    """
    If object contains image -> get this image from server. Check if this image is already in telegram and bot db.
    If so, send message with it`s id. If not - send message and save image`s 'id' in db

        * This is useful, because telegram contains media`s id`s, so we can just pass this id to message
    """
    file_path = resp.get(image_key)
    filename = file_path.split('/')[-1]
    file_data = await File.get_or_none(filename=filename, parent_id=pk)
    if not file_data:
        resp_file = await Conn.get(file_path, user_id=call.from_user.id)
        msg = await call.bot.send_photo(chat_id=call.from_user.id,
                                        photo=resp_file.get('file'), caption=text,
                                        reply_markup=keyboard)
        await File.create(filename=filename, parent_id=pk,
                          file_id=msg.photo[-1].file_id)
    else:
        await call.bot.send_photo(chat_id=call.from_user.id,
                                  photo=file_data.file_id,
                                  caption=text, reply_markup=keyboard)


async def update_state(state: FSMContext, new_data: Union[int, str, dict],
                       key: str, root_key: str):
    log.info(f'{new_data} - {key}')
    async with state.proxy() as data:
        data.setdefault(root_key, {})[key] = new_data
