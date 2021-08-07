from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp

from keyboards.default.dispatcher import dispatcher

from middlewares import _


@dp.message_handler(Text(equals=['Настройки', 'Settings']))
async def user_settings(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_SETTINGS', message.from_user.id)
    await message.answer(_('Настройки пользователя'), reply_markup=keyboard)
    await state.update_data(path=path)
