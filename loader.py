import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage

from data import config

from utils.session.session_manager import SessionManager

from tortoise import Tortoise

from logger import get_logger


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage(config.REDIS_HOST, 6379, db=5)
dp = Dispatcher(bot, storage=storage)
Conn = SessionManager()
db = Tortoise()
log = get_logger()

logging.basicConfig(filemode='app.log',)


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
