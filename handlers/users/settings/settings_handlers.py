import logging
from aiohttp.client_exceptions import ContentTypeError

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher

from middlewares import _
from utils.db_api.models import User

from utils.session.url_dispatcher import REL_URLS

from data.config import PAYMENT_PROVIDER_TOKEN

from states.state_groups import Subscription


Subscription_price = types.LabeledPrice(label=_('Пользовательская подписка'), amount=1000)


@dp.message_handler(Text(equals=['Настройки', 'Settings']))
async def user_settings(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_SETTINGS', message.from_user.id)
    await message.answer(_('Настройки пользователя'), reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Настройки подписки', 'Subscription']))
async def subscription_settings(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_3_SUBSCRIPTION', message.from_user.id)
    await message.answer(_('Премиум подписка'), reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Получить подписку', 'Subscribe']))
async def get_subscription(message: types.Message):
    user = await User.get(user_id=message.from_user.id)
    url = f'{REL_URLS["users"]}{user.swipe_id}/'
    resp = await Conn.get(url, user_id=user.user_id)
    if resp.get('subscribed') is True:
        await message.answer(_('У вас уже оформлена подписка.\n' +
                               'Она закончится - {end_date}').format(end_date=resp.get('end_date')))
    else:
        await message.answer(_('Вы можете оформить подписку за 1 грн. \n'
                               '<b>**Для тестировщиков:**</b> Платежи <b>тестовые</b>.\n' +
                               'Никакие суммы взыматься не будут'))
        await message.answer(_('Можете использовать следующие данные платежной карты: \n' +
                               'Номер: 4242 4242 4242 4242\n' +
                               'Дата: 01/22\n' +
                               'CVV: 123'))
        text = _('Пользовательская подписка дает преимущества на тех кто ищет, и тех кто продает')
        await message.bot.send_invoice(
            message.chat.id,
            title=_('Пользовательская подписка'),
            description=text,
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency='uah',
            is_flexible=False,
            prices=[Subscription_price],
            start_parameter='user-subscription',
            payload='some-invoice-payload-for-our-internal-use'
        )
        await Subscription.PAYMENT.set()


@dp.pre_checkout_query_handler(state=Subscription.PAYMENT)
async def process_pre_checkout_query_subscribe(query: types.PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT, state=Subscription.PAYMENT)
async def process_successful_payment_subscription(message: types.Message, state: FSMContext):
    logging.info('successful_payment')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        logging.info(f'{key} = {val}')

    user = await User.get(user_id=message.from_user.id)
    url = REL_URLS['subscription'].format(pk=user.swipe_id)
    data = {'subscribed': '1'}
    try:
        resp = await Conn.patch(url, data=data, user_id=user.user_id)
        if resp.get('subscribed') is True:
            await message.answer(_('Оплата прошла успешно.\n' +
                                   'Ваша подписка активирована до {date}').format(date=resp.get('end_date')))
        else:
            await message.answer(_('Произошла ошибка. Попробуйте ещё раз'))
        data = await state.get_data()
        await state.finish()
        await state.update_data(**data)
    except ContentTypeError:
        await message.answer(_('Произошла ошибка. Попробуйте ещё раз'))
        data = await state.get_data()
        await state.finish()
        await state.update_data(**data)


@dp.message_handler(Text(equals=['Проверить статус подписки', 'Check subscription status']))
async def check_subscription(message: types.Message):
    user = await User.get(user_id=message.from_user.id)
    url = f'{REL_URLS["users"]}{user.swipe_id}/'
    resp = await Conn.get(url, user_id=user.user_id)
    if resp.get('subscribed') is True:
        await message.answer(_('Ваша пользовательская подписка активирована до {date}').format(date=resp.get('end_date')))
    else:
        await message.answer(_('Ваша пользовательская подписка не активирована'))


@dp.message_handler(Text(equals=['Отменить подписку', 'Cancel subscription']))
async def cancel_subscription(message: types.Message):
    user = await User.get(user_id=message.from_user.id)
    url = REL_URLS['subscription'].format(pk=user.swipe_id)
    data = {'subscribed': '0'}
    resp = await Conn.patch(url, data=data, user_id=user.user_id)
    if resp.get('subscribed') is False:
        await message.answer(_('Ваша пользовательская подписка отменена'))
    else:
        await message.answer(_('Произошла ошибка. Повторите попытку'))
