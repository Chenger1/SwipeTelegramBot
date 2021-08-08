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


class CreateHouse(StatesGroup):
    STARTER = State()
    NAME = State()
    CITY = State()
    ADDRESS = State()
    TECH = State()
    TERR = State()
    PAYMENT_OPTIONS = State()
    DESCRIPTION = State()

    SAVE = State()

    #  This states is optional
    ROLE = State()
    TYPE = State()
    HOUSE_CLASS = State()
    SEA = State()
    HEIGHT = State()
    GAS = State()
    HEATING = State()
    ELECTRICITY = State()
    SEWERAGE = State()
    WATER = State()
    PLAYGROUND = State()
    CAR_PARK = State()
    SHOP = State()
    CHILD_PLAYGROUND = State()
    ELEVATOR = State()
    SECURITY = State()
    IMAGE = State()


class EditUserDate(StatesGroup):
    STARTER = State()
    NAME = State()
    EMAIL = State()
    PHOTO = State()
    ROLE = State()
    SAVE = State()


class Subscription(StatesGroup):
    PAYMENT = State()
