from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from middlewares import _


async def get_user_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Список публикаций')),
        KeyboardButton(_('Список домов'))
    ).row(
        KeyboardButton(_('Избранное'))
    ).row(
        KeyboardButton(_('Входящие запросы на добавление в шахматку'))
    ).row(
        KeyboardButton(_('Настройки'))
    )
    return markup


async def get_level_2_post_keyboard(is_admin) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Вернуться')),
    ).add(
        KeyboardButton(_('Фильтрация объявлений'))
    ).add(
        KeyboardButton(_('Текущие фильтры')),
        KeyboardButton(_('Мои фильтры')),
        KeyboardButton(_('Сбросить фильтры'))
    ).add(
        KeyboardButton(_('Добавить новую публикацию')),
        KeyboardButton(_('Мои объявления'))
    )
    return markup


async def get_level_2_filter_post_keyboard(is_admin) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Фильтровать'))
    ).add(
        KeyboardButton(_('Перейти к цене'))
    ).add(
        KeyboardButton(_('Перейти к площади'))
    ).add(
        KeyboardButton(_('Перейти к городу'))
    ).add(
        KeyboardButton(_('Перейти к состоянию квартиры'))
    ).add(
        KeyboardButton(_('Перейти к планировке'))
    ).add(
        KeyboardButton(_('Перейти к территории'))
    ).add(
        KeyboardButton(_('Вернуться')),
        KeyboardButton(_('Сохранить фильтр'))
    )
    return markup


async def get_level_3_create_post_keyboard(is_admin) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к дому')),
        KeyboardButton(_('Перейти к квартире'))
    ).add(
        KeyboardButton(_('Перейти к цене')),
        KeyboardButton(_('Перейти к способу платежа'))
    ).add(
        KeyboardButton(_('Перейти к вариантам связи'))
    ).add(
        KeyboardButton(_('Перейти к описанию')),
        KeyboardButton(_('Перейти к фото'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )
    return markup


async def get_level_2_house_keyboard(is_admin: int) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Все дома'))
    ).add(
        KeyboardButton(_('Мои квартиры')),
        KeyboardButton(_('Мои дома'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )
    return markup


async def get_level_3_my_house_keyboard(is_admin: int) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Добавить дом'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )
    return markup


async def get_level_4_create_house(is_admin: int) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к названию')),
        KeyboardButton(_('Перейти к городу')),
        KeyboardButton(_('Перейти к адресу'))
    ).add(
        KeyboardButton(_('Перейти к технологии строительства')),
        KeyboardButton(_('Перейти к территории'))
    ).add(
        KeyboardButton(_('Перейти к платежным способами')),
        KeyboardButton(_('Перейти к описанию'))
    ).add(
        KeyboardButton(_('Перейти к статусу')),
        KeyboardButton(_('Перейти к типу')),
        KeyboardButton(_('Перейти к классу дома')),
    ).add(
        KeyboardButton(_('Перейти к расстоянию до моря')),
        KeyboardButton(_('Перейти к высоте потолков'))
    ).add(
        KeyboardButton(_('Перейти к газопроводу')),
        KeyboardButton(_('Перейти к отоплению')),
        KeyboardButton(_('Перейти к электричеству')),
        KeyboardButton(_('Перейти к канализации')),
        KeyboardButton(_('Перейти к водоснабжению'))
    ).add(
        KeyboardButton(_('Перейти к спортивной площадке')),
        KeyboardButton(_('Перейти к парковке')),
        KeyboardButton(_('Перейти к магазину')),
        KeyboardButton(_('Перейти к детской площадке')),
        KeyboardButton(_('Перейти к лифту')),
        KeyboardButton(_('Перейти к охране'))
    ).add(
        KeyboardButton(_('Перейти к картинке'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )
    return markup


async def get_level_2_user_settings_keyboard(is_admin: int) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Изменить данные')),
        KeyboardButton(_('Настройки подписки')),
        KeyboardButton(_('Язык'))
    )
    if is_admin:
        markup.add(
            KeyboardButton(_('Отключить режим администратора'))
        )
    else:
        markup.add(
            KeyboardButton(_('Ввести токен администратора'))
        )
    markup.add(
        KeyboardButton(_('Вернуться'))
    )
    return markup


async def get_level_2_admin_panel(is_admin: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Список нотариусов')),
        KeyboardButton(_('Жалобы'))
    ).add(
        KeyboardButton(_('Рассылка'))
    ).add(
        KeyboardButton(_('Получить логи')),
        KeyboardButton(_('Получить список пользователей')),
    ).add(
        KeyboardButton(_('Вернуться'))
    )


async def get_level_3_user_settings_edit_data(is_admin: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к имени и фамилии')),
        KeyboardButton(_('Перейти к электронной почте'))
    ).add(
        KeyboardButton(_('Перейти к фото')),
        KeyboardButton(_('Перейти к роли'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )


async def get_level_3_user_subscription_settings(is_admin: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Получить подписку')),
        KeyboardButton(_('Проверить статус подписки'))
    ).add(
        KeyboardButton(_('Вернуться'))
    ).add(
        KeyboardButton(_('Отменить подписку'))
    )


async def get_level_3_add_promotion(is_admin: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к фразе')),
        KeyboardButton(_('Перейти к типу'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )


async def get_level_4_add_flat(is_admin: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к этажу'))
    ).add(
        KeyboardButton(_('Перейти к номеру')),
        KeyboardButton(_('Перейти к площади')),
        KeyboardButton(_('Перейти к площади кухи'))
    ).add(
        KeyboardButton(_('Перейти к цене')),
        KeyboardButton(_('Перейти к цене за кв. метр')),
        KeyboardButton(_('Перейти к числу комнат'))
    ).add(
        KeyboardButton(_('Перейти к состоянию')),
        KeyboardButton(_('Перейти к типу собственности')),
    ).add(
        KeyboardButton(_('Перейти к типу')),
        KeyboardButton(_('Перейти к балкону')),
        KeyboardButton(_('Перейти к отоплению'))
    ).add(
        KeyboardButton(_('Перейти к схеме'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )


async def get_level_4_add_news(is_admin: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к заголовку')),
        KeyboardButton(_('Перейти к описанию'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )


async def get_level_4_add_doc(is_admin: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Сохранить'))
    ).add(
        KeyboardButton(_('Перейти к названию')),
        KeyboardButton(_('Перейти к файлу'))
    ).add(
        KeyboardButton(_('Вернуться'))
    )
