import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN

from session_manager import SessionManager
from utils import representation
from db import DB


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
database = DB()
session_manager = SessionManager(database)

post_agent = representation.PostRepresentationAgent()
house_agent = representation.HouseRepresentationAgent()
flat_agent = representation.FlatRepresentationAgent()
