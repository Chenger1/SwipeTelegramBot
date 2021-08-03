import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from states.state_groups import FilterPost

from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline import filter_post
from keyboards.callbacks.user_callback import POST_FILTER_CB

from handlers.users.post.public_post import handle_posts

from middlewares import _


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=FilterPost)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    await state.finish()
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Перейти к цене', 'Go to price']), state=FilterPost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = 'Текущая цена <b>{price__gte}:{price__lte}</b>'.format(price__gte=data.get('price__gte', _('Не указано')),
                                                                  price__lte=data.get('price__lte', _('Не указано')))
    await message.answer(_(text))
    await message.answer(_('Введите новое значение цены для поиска'))
    await FilterPost.PRICE.set()


@dp.message_handler(Text(equals=['Перейти к площади', 'Go to square']), state=FilterPost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = 'Текущая площадь <b>{square__gte}:{square__lte}</b>'.\
        format(square__gte=data.get('flat__square__gte', _('Не указано')),
               square__lte=data.get('flat__square__lte', _('Не указано')))
    await message.answer(_(text))
    await message.answer(_('Введите новое значение площади для поиска'))
    await FilterPost.SQUARE.set()


@dp.message_handler(Text(equals=['Перейти к городу', 'Go to city']), state=FilterPost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = 'Текущая город <b>{city}</b>'.format(city=data.get('house__city', _('Не указано')))
    await message.answer(_(text))
    await message.answer(_('Введите новый город для поиска'))
    await FilterPost.CITY.set()


@dp.message_handler(Text(equals=['Перейти к состоянию квартиры', 'Go to flat state']), state=FilterPost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    labels = filter_post.labels
    text = 'Выбранное состояние <b>{state}</b>'.format(state=labels.get(data.get('flat__state'), _('Не указано')))
    await message.answer(_(text))
    await message.answer(_('Выберите новое состояние для поиска'),
                         reply_markup=await filter_post.get_filter_post_state_keyboard())
    await FilterPost.STATE.set()


@dp.message_handler(Text(equals=['Перейти к планировке', 'Go to flat plan']), state=FilterPost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    labels = filter_post.labels
    text = 'Выбранная планировка <b>{plan}</b>'.format(plan=labels.get(data.get('flat__plan'), _('Не указано')))
    await message.answer(_(text))
    await message.answer(_('Выберите новую планировку для поиска'),
                         reply_markup=await filter_post.get_filter_post_plan_keyboard())
    await FilterPost.PLAN.set()


@dp.message_handler(Text(equals=['Перейти к территории', 'Go to territory']), state=FilterPost)
async def go_to_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    labels = filter_post.labels
    text = 'Выбранная территория <b>{terr}</b>'.format(terr=labels.get(data.get('house__territory'), _('Не указано')))
    await message.answer(_(text))
    await message.answer(_('Выберите новую территорию для поиска'),
                         reply_markup=await filter_post.get_filter_post_territory_keyboard())
    await FilterPost.TERR.set()


@dp.message_handler(Text(equals=['Фильтровать', 'Filter']), state=FilterPost)
async def go_to_filter(message: types.Message, state: FSMContext):
    data = await state.get_data()
    labels = filter_post.labels
    no_data = _('Не указано')
    text = '<b>Цена</b> {price__gte}:{price__lte} грн\n' \
           '<b>Площадь</b> {square__gte}:{square__lte} м2\n' \
           '<b>Город</b>: {city}\n <b>Состояние</b> {state}\n' \
           '<b>Территория</b>: {terr}\n <b>Планировка</b> {plan}'. \
        format(price__gte=data.get('price__gte', no_data),
               price__lte=data.get('price__lte', no_data),
               square__gte=data.get('flat__square__gte', no_data),
               square__lte=data.get('flat__square__lte', no_data),
               city=data.get('house__city', no_data),
               state=labels.get(data.get('flat__state'), no_data),
               terr=labels.get(data.get('house__territory'), no_data),
               plan=labels.get(data.get('flat__plan'), no_data))
    await message.answer(_(text))
    await message.answer(_('Подтвердите'), reply_markup=await filter_post.get_filter_post_confirm_keyboard())
    await FilterPost.FILTERING.set()


@dp.message_handler(Text(equals=['Фильтрация объявлений', 'Filter ads']))
async def filter_post_handler(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_3_FILTER_POSTS', message.from_user.id)
    await message.answer(text=_('Заполните форму для фильтрации'), reply_markup=keyboard)
    await state.update_data(path=path)
    logging.info({'path': path})
    await message.answer(text=_('Укажите цену в формате от:до'))
    await FilterPost.PRICE.set()


@dp.message_handler(state=FilterPost.PRICE)
async def filter_price(message: types.Message, state: FSMContext):
    answer = message.text
    try:
        price__gte, price__lte = answer.split(':')
        if (price__gte == '' or isinstance(int(price__gte), int)) \
                and (price__lte == '' or isinstance(int(price__lte), int)):
            await state.update_data(price__gte=price__gte,
                                    price__lte=price__lte)
        await message.answer(_('Введите площадь в формате "от:до"'))
        await FilterPost.SQUARE.set()
    except ValueError:
        await message.answer('Неправильный формат ввода')


@dp.message_handler(state=FilterPost.SQUARE)
async def filter_square(message: types.Message, state: FSMContext):
    answer = message.text
    try:
        square__gte, square__lte = answer.split(':')
        if (square__gte == '' or isinstance(int(square__gte), int)) \
                and (square__lte == '' or isinstance(int(square__lte), int)):
            await state.update_data(flat__square__gte=square__gte,
                                    flat__square__lte=square__lte)
            await message.answer(_('Введите город'))
            await FilterPost.CITY.set()
    except ValueError:
        await message.answer(_('Неправильнй формат ввода'))


@dp.message_handler(state=FilterPost.CITY)
async def filter_city(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(house__city=answer)
    await message.answer(_('Укажите желаемое состояние квартиры'),
                         reply_markup=await filter_post.get_filter_post_state_keyboard())
    await FilterPost.STATE.set()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='filter_state'), state=FilterPost.STATE)
async def filter_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    await state.update_data(flat__state=value)
    await call.answer()
    await call.message.answer(_('Выберите желаемый тип территории'),
                              reply_markup=await filter_post.get_filter_post_territory_keyboard())
    await FilterPost.TERR.set()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='filter_territory'), state=FilterPost.TERR)
async def filter_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    await state.update_data(house__territory=value)
    await call.answer()
    await call.message.answer(_('Выберите желаемый тип планировки'),
                              reply_markup=await filter_post.get_filter_post_plan_keyboard())
    await FilterPost.PLAN.set()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='filter_plan'), state=FilterPost.PLAN)
async def filter_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    await state.update_data(flat__plan=value)
    await call.answer()
    data = await state.get_data()
    labels = filter_post.labels
    no_data = _('Не указано')
    text = '<b>Цена</b> {price__gte}:{price__lte} грн\n' \
           '<b>Площадь</b> {square__gte}:{square__lte} м2\n' \
           '<b>Город</b>: {city}\n <b>Состояние</b> {state}\n' \
           '<b>Территория</b>: {terr}\n <b>Планировка</b> {plan}'.\
        format(price__gte=data.get('price__gte', no_data),
               price__lte=data.get('price__lte', no_data),
               square__gte=data.get('flat__square__gte', no_data),
               square__lte=data.get('flat__square__lte', no_data),
               city=data.get('house__city', no_data),
               state=labels.get(data.get('flat__state'), no_data),
               terr=labels.get(data.get('house__territory'), no_data),
               plan=labels.get(data.get('flat__plan'), no_data))
    await call.message.answer(_(text))
    await call.message.answer(_('Подтвердите'), reply_markup=await filter_post.get_filter_post_confirm_keyboard())
    await call.answer()
    await FilterPost.FILTERING.set()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='filter_confirm'), state=FilterPost.FILTERING)
async def filter_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logging.info(callback_data)
    value = callback_data.get('value')
    if value == 'YES':
        params = await state.get_data()
        keyboard, path = await dispatcher('LEVEL_2_POSTS', call.from_user.id)
        await handle_posts(call, page='1', key='posts_public', keyboard=keyboard, params=params,
                           new=True)
        await state.finish()
        await state.update_data(path=path)
    else:
        await call.message.answer(_('Используйте меню чтобы выбрать етап фильтрации'))
    await call.answer()
