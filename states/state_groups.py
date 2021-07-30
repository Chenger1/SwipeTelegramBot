from aiogram.dispatcher.filters.state import State, StatesGroup


class StartState(StatesGroup):
    PHONE = State()
    CHECK_TOKEN = State()
