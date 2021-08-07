from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp

from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label

from middlewares import _

from states.state_groups import EditUserDate


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=EditUserDate)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    if data.get('edit_data'):
        data.pop('edit_data')
    await state.finish()
    data['path'] = path
    await state.update_data(**data)


@dp.message_handler(Text(equals=['Изменить данные', 'Change data']))
async def edit_data(message: types.Message, state: FSMContext):
    await EditUserDate.STARTER.set()
    keyboard, path = await dispatcher('LEVEL_3_EDIT_DATA', message.from_user.id)
    await message.answer(_('Введите имя и фамилию через пробел'), reply_markup=keyboard)
    await state.update_data(path=path)
    await EditUserDate.NAME.set()
