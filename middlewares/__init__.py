from aiogram import Dispatcher

from data.config import I18N_DOMAIN, LOCALES_DIR

from loader import dp
from .throttling import ThrottlingMiddleware
from .language import ACLMiddleware


def setup_middleware():
    # Устанавливаем миддлварь
    i18n_ = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n_)
    return i18n_


i18n = setup_middleware()
_ = i18n.gettext


if __name__ == "middlewares":
    dp.middleware.setup(ThrottlingMiddleware())
