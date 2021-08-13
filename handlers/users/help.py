from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp

from middlewares import _


@dp.message_handler(CommandHelp(), state='*')
async def bot_help(message: types.Message):
    text = _("Список команд: \n" +
             "/start - Начать диалог\n" +
             "/help - Получить справку\n" +
             'SwipeTelegramBot поможет вам получить информацию об актуальных предложениях аренды')
    
    await message.answer(text)
