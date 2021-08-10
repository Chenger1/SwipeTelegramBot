import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from data.config import PAYMENT_PROVIDER_TOKEN
from loader import dp, Conn

from keyboards.callbacks.user_callback import DETAIL_CB, POST_FILTER_CB as ITEM_CB
from keyboards.default.dispatcher import dispatcher, get_menu_label, back_button
from keyboards.inline.create_promotion import phrase_keyboard, get_promotion_type_keyboard
from keyboards.inline.create_house import confirm_keyboard

from states.state_groups import CreatePromotion
from handlers.users.utils import update_state

from utils.session.url_dispatcher import REL_URLS

from middlewares import _

prices = {}


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=CreatePromotion)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    keys_to_delete = ('create_promotion',)
    new_dict = {}
    for key, value in data.items():
        if key not in keys_to_delete:
            new_dict[key] = value
    await state.finish()
    new_dict['path'] = path
    await state.update_data(**new_dict)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=CreatePromotion)
async def save_promotion_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get('create_promotion')
    keys = ('phrase', 'type', 'post')
    if all(key in post_data for key in keys):
        text = _('Подтверждаете?')
        await message.answer(text, reply_markup=confirm_keyboard)
        await CreatePromotion.SAVE.set()
    else:
        text = _('Вы не указали: \n')
        if not post_data.get('phrase'):
            text += _('Фразу\n')
        if not post_data.get('type'):
            text += _('Тип\n')
        await message.answer(text)


@dp.message_handler(Text(equals=['Перейти к фразе', 'Go to phrase']), state=CreatePromotion)
async def go_to_phrase(message: types.Message):
    await message.answer(_('Выберите фразу'), reply_markup=phrase_keyboard)
    await CreatePromotion.PHRASE.set()


@dp.message_handler(Text(equals=['Перейти к типу', 'Go to type']), state=CreatePromotion)
async def go_to_type(message: types.Message):
    resp = await Conn.get(REL_URLS['promotion_types'], user_id=message.from_user.id)
    await message.answer(_('Выберите тип продвижения'),
                         reply_markup=await get_promotion_type_keyboard(resp.get('results')))
    text = ''
    for index, item in enumerate(resp.get('results'), start=1):
        prices[item['id']] = types.LabeledPrice(label=item['name'], amount=(int(item['price']) * 50) + 500)
        text += _('{index}. {name}.\n Эффективность {efficiency}\n ' +
                  'Цена {price} грн.\n').format(index=index, name=item['name'],
                                                efficiency=item['efficiency'],
                                                price=item['price'])
    await message.answer(text)
    await CreatePromotion.TYPE.set()


@dp.callback_query_handler(DETAIL_CB.filter(action='add_promotion'))
async def add_promotion(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await CreatePromotion.STARTER.set()
    pk = callback_data.get('pk')
    keyboard, path = await dispatcher('LEVEL_3_ADD_PROMOTION', call.from_user.id)
    await call.message.answer(_('Заказ продвижения объявления\n' +
                                'Фраза: 50 грн'), reply_markup=keyboard)
    await call.message.answer(_('Выберите специальную фразу'), reply_markup=phrase_keyboard)
    await CreatePromotion.PHRASE.set()
    await update_state(state, pk, 'post', 'create_promotion')
    await state.update_data(path=path)
    await call.answer()


@dp.callback_query_handler(ITEM_CB.filter(action='add_phrase'), state=CreatePromotion.PHRASE)
async def add_promotion_phrase(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'phrase', 'create_promotion')

    resp = await Conn.get(REL_URLS['promotion_types'], user_id=call.from_user.id)
    await call.message.answer(_('Выберите тип'), reply_markup=await get_promotion_type_keyboard(resp.get('results')))
    text = ''
    for index, item in enumerate(resp.get('results'), start=1):
        prices[item['id']] = types.LabeledPrice(label=item['name'], amount=(int(item['price']) * 50) + 500)
        text += _('{index}. {name}.\n Эффективность {efficiency}\n ' +
                  'Цена {price} грн.').format(index=index, name=item['name'],
                                              efficiency=item['efficiency'],
                                              price=item['price'])
    await call.message.answer(text)
    await call.answer()
    await CreatePromotion.TYPE.set()


@dp.callback_query_handler(ITEM_CB.filter(action='add_type'), state=CreatePromotion.TYPE)
async def add_promotion_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'type', 'create_promotion')
    await call.message.answer(_('Подтверждаете?'), reply_markup=confirm_keyboard)
    await CreatePromotion.SAVE.set()


@dp.callback_query_handler(ITEM_CB.filter(action='create_confirm'), state=CreatePromotion.SAVE)
async def save_promotion(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    if value:
        state_data = await state.get_data()
        promo_data = state_data.get('create_promotion')
        promo_data['paid'] = False
        resp, status = await Conn.post(REL_URLS['promotions'], data=promo_data, user_id=call.from_user.id)
        if status == 201:
            await call.answer(_('Необходимо оплатить заказ'), show_alert=True)
            await call.message.answer(_('Можете использовать следующие данные тестовой платежной карты: \n' +
                                        'Номер: 4242 4242 4242 4242\n' +
                                        'Дата: 01/22\n' +
                                        'CVV: 123'))

            await call.bot.send_invoice(
                call.message.chat.id,
                title=_('Оплата заказа на продвижение объявления'),
                description=_('Без оплаты продвижения не случится'),
                provider_token=PAYMENT_PROVIDER_TOKEN,
                currency='uah',
                is_flexible=False,
                prices=[prices[int(promo_data.get('type'))]],
                start_parameter='post_promotion',
                payload='some-invoice-payload-for-our-internal-use'
            )
            await CreatePromotion.PAYMENT.set()
            await update_state(state, resp['id'], 'promotion_pk', 'create_promotion')
    else:
        await call.answer(_('Вы можете выбрать этап через меню'))


@dp.pre_checkout_query_handler(state=CreatePromotion.PAYMENT)
async def process_pre_checkout_query_subscribe(query: types.PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT, state=CreatePromotion.PAYMENT)
async def process_successful_promotion_payment(message: types.Message, state: FSMContext):
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        logging.info(f'{key} = {val}')

    state_data = await state.get_data()
    promo_data = state_data.get('create_promotion')
    url = f'{REL_URLS["promotions"]}{promo_data.get("promotion_pk")}/'
    resp = await Conn.patch(url, data={'paid': True}, user_id=message.from_user.id)
    if resp.get('paid'):
        state_data.pop('create_promotion')
        resp_detail = await Conn.get(url, user_id=message.from_user.id)
        await message.answer(_('Продвижение успешно заказано до {date}').format(date=resp_detail.get('end_date')))
        await state.finish()
        await state.update_data(**state_data)

    else:
        await message.answer(_('Произошла ошибка'))
        for key, value in resp.items():
            logging.info(f'{key} - {value}')
