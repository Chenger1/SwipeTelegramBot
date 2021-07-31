from aiogram import types

from middlewares import _


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", _('Запустить бота')),
            types.BotCommand("help", _('Вывести справку')),
            types.BotCommand("cancel", _('Отменить/Пропустить'))
        ]
    )
