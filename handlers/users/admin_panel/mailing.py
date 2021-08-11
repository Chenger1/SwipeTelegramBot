import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text
from aiogram.utils import exceptions

from loader import dp, log

from states.state_groups import Mailing

from middlewares import _

from utils.db_api.models import User


async def send_message(user_id: int, text: str, bot) -> bool:
    try:
        await bot.send_message(user_id, text)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text, bot)
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.error(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


@dp.message_handler(Text(equals=['Рассылка', 'Mailing']), is_admin=True)
async def mailing(message: types.Message):
    await Mailing.STARTER.set()
    await message.answer(_('Введите сообщение для отправки'))
    await Mailing.TEXT.set()


@dp.message_handler(state=Mailing.TEXT)
async def broadcast(message: types.Message, state: FSMContext):
    text = message.text
    count = 0
    try:
        for user in await User.all():
            if await send_message(user.user_id, text, message.bot):
                count +=1
            await asyncio.sleep(.05)
    finally:
        log.info(f'{count} messages successful sent.')
    state_data = await state.get_data()
    await state.finish()
    await state.update_data(**state_data)
