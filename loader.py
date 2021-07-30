from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config

from utils.session.session_manager import SessionManager

from tortoise import Tortoise


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
Conn = SessionManager()
db = Tortoise()


TORTOISE_ORM = {
    'connections': {
        'default': 'sqlite://db.sqlite3'
    },
    'apps': {
        'models': {
            'models': ['utils.db_api.models', 'aerich.models'],
            'default_connection': 'default'
        }
    }
}
