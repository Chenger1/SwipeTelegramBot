from aiogram.dispatcher.filters.state import StatesGroup, State


class PostFilter(StatesGroup):
    CITY = State()
    PRICE = State()
    SQUARE = State()
    FILTERING = State()
