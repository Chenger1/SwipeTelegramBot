from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher

from filters.admin import IsAdmin

from middlewares import _


@dp.message_handler(Text(equals=['Панель администратора', 'Admin Panel']), is_admin=True)
async def admin_panel(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_ADMIN_PANEL', message.from_user.id)
    await message.answer(_('Панель администратора'), reply_markup=keyboard)
    await state.update_data(path=path)



