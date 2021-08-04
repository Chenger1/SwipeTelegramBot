from aiogram.dispatcher.filters.state import State, StatesGroup


class StartState(StatesGroup):
    PHONE = State()
    LANG = State()
    CHECK_TOKEN = State()


class FilterPost(StatesGroup):
    PRICE = State()
    SQUARE = State()
    CITY = State()
    STATE = State()
    PLAN = State()
    TERR = State()
    FILTERING = State()
    SAVE_FILTER = State()  # Optional


class CreatePost(StatesGroup):
    STARTER = State()
    HOUSE = State()
    FLAT = State()
    PAYMENT = State()
    PRICE = State()
    COMMUNICATION = State()
    DESCRIPTION = State()
    IMAGE = State()
    SAVE = State()
