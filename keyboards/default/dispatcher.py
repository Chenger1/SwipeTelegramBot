from typing import Callable, Tuple

from aiogram.types import ReplyKeyboardMarkup

from keyboards.default import user_keyboards, admin_keyboards

from utils.db_api.models import User

from middlewares import _


menu_storage = {
    'LEVEL_1': admin_keyboards.keyboard_dispatcher,
    'LEVEL_1:LEVEL_2': {
        'LEVEL_2_POSTS': user_keyboards.get_level_2_post_keyboard,
        'LEVEL_2_POSTS:LEVEL_3_FILTER_POSTS': {
            'LEVEL_3_FILTER_POSTS': user_keyboards.get_level_2_filter_post_keyboard,
            'LEVEL_3_CREATE_POST': user_keyboards.get_level_3_create_post_keyboard
        },
        'LEVEL_2_HOUSES': user_keyboards.get_level_2_house_keyboard,
        'LEVEL_2_HOUSES:LEVEL_3_MY_HOUSES': {
            'LEVEL_3_MY_HOUSES': user_keyboards.get_level_3_my_house_keyboard,
            'LEVEL_3_MY_HOUSES:LEVEL_4_ADD_HOUSE': {
                'LEVEL_4_ADD_HOUSE': user_keyboards.get_level_4_create_house
            }
        },
        'LEVEL_2_SETTINGS': user_keyboards.get_level_2_user_settings_keyboard,
        'LEVEL_2_SETTINGS:LEVEL_3_EDIT_DATA': {
            'LEVEL_3_EDIT_DATA': user_keyboards.get_level_3_user_settings_edit_data
        }
    }
}
menu_label = {
    'LEVEL_1': _('Главное меню'),
    'LEVEL_2_POSTS': _('Список публикаций'),
    'LEVEL_3_FILTER_POSTS': _('Фильтрация объявлений'),
    'LEVEL_2_HOUSES': _('Дома'),
}


async def dispatcher(level: str, user_id: int) -> Tuple[ReplyKeyboardMarkup, str]:
    """
     Checks if user is admin. Returns right keyboard for each level and group
     """
    user = await User.get_or_none(user_id=user_id)
    if user:
        is_admin = user.is_admin
    else:
        is_admin = False
    keyboard_cor, path = await find_in_dict(level, menu_storage)
    return await keyboard_cor(is_admin), path


async def find_in_dict(level: str, storage: dict, path: str = '') -> Tuple[Callable, str]:
    """
    RECURSIVE function.
    Iterates over storage. If key == level and key`s value is Callable - return this callable (coroutine)
    If not, check if key`s value is dictionary. Dictionary is a sublevel.
    So, we run recursive coroutine and pass - level, THIS KEY`S VALUE - that is i mean sublevel
    And current path.
    If this coroutine returns result - return it on top. Other wire continue iteration
    :param level: Level we want to reach
    :param storage: menu_storage
    :param path: path for current level from top of the menu_storage. Uses in back_button
    """
    for key, value in storage.items():
        if key == level and isinstance(value, Callable):
            path += f'/{key}'
            return value, path
        if isinstance(value, dict):
            path += f'/{key}'
            result = await find_in_dict(level, value, path)
            if result:
                return result
            path = '/'.join(path.split('/')[:-1])
            #  if we didn't find the result - remove this path and iterate again


async def back_button(path: str, user_id: int) -> Tuple[ReplyKeyboardMarkup, str]:
    """
    Path looks like 'LEVEL_1:LEVEL_2/LEVEL_2_POSTS'. Split string to get previous level.
    Previous level ALWAYS has format 'LEVEL_1:LEVEL_2'. Split it to get 'LEVEL_1' - this level we want to rich to
    got back
    Pass this level to dispatcher
    :param path: path to current level
    :param user_id: user id in telegram. Need for check for admin permissions
    :return: ReplyKeyboardMarkup
    """
    levels = path.split('/')
    last_level = levels[-2].split(':')[0]
    return await dispatcher(last_level, user_id)


async def get_menu_label(path: str) -> str:
    """
    Telegram doesnt allow to change keyboard with empty text.
    So, for better user experience send simple level 'labels' or 'names'
    :param path: 'LEVEL_1:LEVEL_2/LEVEL_2_POSTS'
    """
    levels = path.split('/')
    return menu_label.get(levels[-1], _('Возврат'))
