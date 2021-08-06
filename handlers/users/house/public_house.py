from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp

from keyboards.default.dispatcher import dispatcher

from deserializers.house import HouseDeserializer

from middlewares import _


house_des = HouseDeserializer()


@dp.message_handler(Text(equals=['Список домов', 'House list']))
async def get_house_keyboard(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_3_HOUSE', message.from_user.id)
    await message.answer(_('Меню домов'), reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Все дома', 'Houses']))
async def house_list(message: types.Message, state: FSMContext):
    pass
