from aiogram import executor

from loader import dp

import handlers

# CONST
WEBHOOK_ENDPOINT = 'http://188.225.43.69:1337'


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
