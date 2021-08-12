from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from loader import dp, Conn, log

from keyboards.default.dispatcher import dispatcher
from keyboards.inline.user_keyboards import lang_markup
from keyboards.callbacks.user_callback import LANG_CB

from middlewares import _
from utils.db_api.models import User

from utils.session.url_dispatcher import REL_URLS

from data.config import PAYMENT_PROVIDER_TOKEN

from states.state_groups import Subscription, InputAdminToken, SetLanguageState


Subscription_price = types.LabeledPrice(label=_('Пользовательская подписка'), amount=1000)


@dp.message_handler(Text(equals=['Настройки', 'Settings']))
async def user_settings(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_SETTINGS', message.from_user.id)
    await message.answer(_('Настройки пользователя'), reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Настройки подписки', 'Subscription settings']))
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
    log.info('successful_payment')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        log.info(f'{key} = {val}')

    user = await User.get(user_id=message.from_user.id)
    url = REL_URLS['subscription'].format(pk=user.swipe_id)
    data = {'subscribed': '1'}
    resp = await Conn.patch(url, data=data, user_id=user.user_id)
    if resp.get('subscribed') is True:
        await message.answer(_('Оплата прошла успешно.\n' +
                               'Ваша подписка активирована до {date}').format(date=resp.get('end_date')))
    else:
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


@dp.message_handler(Text(equals=['Ввести токен администратора', 'Add admin token']))
async def add_admin_token(message: types.Message):
    user = await User.get(user_id=message.from_user.id)
    if user.is_admin:
        await message.answer(_('Вы уже имеете статус администратора'))
    else:
        await InputAdminToken.INPUT.set()
        await message.answer(_('Введите токен'))


@dp.message_handler(state=InputAdminToken.INPUT)
async def check_token(message: types.Message, state: FSMContext):
    answer = message.text
    state_data = await state.get_data()
    user = await User.get(user_id=message.from_user.id)
    url = f'{REL_URLS["users"]}{user.swipe_id}/'
    resp = await Conn.patch(url, data={'is_staff': True, 'admin_token': answer}, user_id=message.from_user.id)
    if resp.get('pk'):
        user.is_admin = True
        await user.save()
        keyboard, path = await dispatcher('LEVEL_2_SETTINGS', message.from_user.id)
        await message.answer(_('Теперь вы имеете статус администратора'), reply_markup=keyboard)
        state_data['path'] = path
    elif resp.get('Token'):
        await message.answer(resp.get('Token'))
    else:
        await message.answer(_('Произошла ошибка'))
        for key, value in resp.items():
            log.info(f'{key} - {value}')
    await state.finish()
    await state.update_data(**state_data)


@dp.message_handler(Text(equals=['Отключить режим администратора', 'Remove admin status']))
async def remove_admin_mode(message: types.Message):
    user = await User.get(user_id=message.from_user.id)
    if user.is_admin:
        await InputAdminToken.SECOND_INPUT.set()
        await message.answer(_('Введите токен'))
    else:
        await message.answer(_('У вас нет статуса администратора'))


@dp.message_handler(state=InputAdminToken.SECOND_INPUT)
async def off_admin_status(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    token = message.text
    user = await User.get(user_id=message.from_user.id)
    url = f'{REL_URLS["users"]}{user.swipe_id}/'
    resp = await Conn.patch(url, data={'is_staff': False, 'admin_token': token}, user_id=message.from_user.id)
    if resp.get('pk'):
        user.is_admin = False
        await user.save()
        keyboard, path = await dispatcher('LEVEL_2_SETTINGS', message.from_user.id)
        await message.answer(_('Вы больше не администратор'), reply_markup=keyboard)
        state_data['path'] = path
    else:
        await message.answer(_('Произошла ошибка'))
        for key, value in resp.items():
            log.info(f'{key} - {value}')
    await state.finish()
    await state.update_data(**state_data)


@dp.message_handler(Text(equals=['Язык', 'Language']))
async def set_language(message: types.Message):
    await message.answer(_('Выберите язык'), reply_markup=lang_markup)


@dp.callback_query_handler(LANG_CB.filter(action='lang'))
async def set_language_callback(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('lang')
    user = await User.get(user_id=call.from_user.id)
    user.language = value
    await user.save()
    await call.answer(_('Язык обновлен. Выйдите этого меню чтобы обновления вступили в силу'), show_alert=True)
