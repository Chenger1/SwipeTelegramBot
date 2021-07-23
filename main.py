from aiogram import executor

from loader import dp, session_manager, bot
from loader import post_agent, house_agent

import handlers


async def on_shutdown():
    session_manager.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)
