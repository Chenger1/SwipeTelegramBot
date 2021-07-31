from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, Conn

from states.state_groups import StartState

from utils.db_api.models import User, AdminToken
from utils.session.url_dispatcher import REL_URLS

from keyboards.default import defaults
from keyboards.default.admin_keyboards import keyboard_dispatcher
from keyboards.callbacks.user_callback import LANG_CB
from keyboards.inline.user_keyboards import lang_markup

from middlewares import _


async def authorize_user(user: User = None,) -> User:
    data = await Conn.authorize(REL_URLS['login'], params={'phone_number': user.phone_number},
                                user_id=user.user_id)
    if data.get('auth'):
        user.token = data.get('auth')
        await user.save()
        return user


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Привет/Hi, {message.from_user.full_name}!")
    await message.answer('Язык/Language', reply_markup=lang_markup)
    await StartState.LANG.set()


@dp.callback_query_handler(LANG_CB.filter(action='lang'), state=StartState.LANG)
async def lang(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    language = callback_data.get('lang')
    await state.set_data({'language': language})
    user = await User.get_or_none(user_id=call.from_user.id)
    if user:
        user.language = language
        await user.save()
    await call.message.answer(_('Отправьте ваш номер для регистрации'),
                              reply_markup=await defaults.get_contact_button())
    await StartState.PHONE.set()


@dp.message_handler(commands=['cancel'], state=StartState)
async def cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await authorize_user(data.get('user'))
    if user:
        await message.answer(_('Вы успешно зарегестрированы в системе'),
                             reply_markup=await keyboard_dispatcher(user.is_admin))
        await state.finish()
    else:
        await message.answer(_('Произошла ошибка. Нажмите /start снова'), reply_markup=defaults.remove_markup)
        await state.reset_state()


@dp.message_handler(content_types=['contact'], state=StartState.PHONE)
async def phone_number(message: types.Message, state: FSMContext):
    if message.content_type != 'contact':
        await message.answer(_('Пожалуйста, отправьте ваш номер для регистрации'))
        return
    data = await state.get_data()
    user, created = await User.get_or_create(user_id=message.from_user.id, phone_number=message.contact.phone_number)
    if user.language != data.get('language'):
        user.language = data.get('language', message.from_user.locale)
        await user.save()
    if user.is_admin:
        result = await authorize_user(user)
        if result:
            await message.answer(_('Вы вошли в систему как администратор'))
            if created:
                await message.answer(_('Вы успешно зарегестрированы в системе'),
                                     reply_markup=await keyboard_dispatcher(user.is_admin))
            else:
                await message.answer(_('Вы уже в системе. Добро пожаловать'))
            await state.finish()
        else:
            await message.answer('Произошла ошибка. Нажмите /start снова')
            await state.reset_state()
    else:
        await state.set_data({'user': user})
        await message.answer(_('Вы можете ввести токен администратора или нажать "/cancel"'),
                             reply_markup=defaults.remove_markup)
        await StartState.CHECK_TOKEN.set()


@dp.message_handler(state=StartState.CHECK_TOKEN)
async def check_admin_token(message: types.Message, state: FSMContext):
    """ If user write token - check it. If token right - set user as admin """
    data = message.text
    if await AdminToken.filter(token=data).exists():
        data = await state.get_data()
        user = data.get('user')
        user.is_admin = True
        result = await authorize_user(user)
        if result:
            await message.answer(_('Вы успешно зарегестрированы в системе'),
                                 reply_markup=await keyboard_dispatcher(user.is_admin))
            await state.finish()
        else:
            await message.answer(_('Произошла ошибка. Нажмите /start снова'))
            await state.reset_state()
    else:
        await message.answer(_('Токен неправильный. Попробуйте снова или нажмите "/cancel"'))
