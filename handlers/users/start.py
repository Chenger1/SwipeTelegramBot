from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, Conn

from states.state_groups import StartState

from utils.db_api.models import User, AdminToken
from utils.session.url_dispatcher import REL_URLS

from keyboards.default import defaults


async def authorize_user(user: User = None,) -> User:
    data = await Conn.authorize(REL_URLS['login'], params={'phone_number': user.phone_number},
                                user_id=user.user_id)
    if data.get('auth'):
        user.token = data.get('auth')
        await user.save()
        return user


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!")
    await message.answer('Для регистрации в системе нужен ваш номер телефона', reply_markup=defaults.contact_markup)
    await StartState.PHONE.set()


@dp.message_handler(text_contains="Пропустить", state=StartState)
async def cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await authorize_user(data.get('user'))
    if user:
        await message.answer('Вы успешно зарегестрированы в системе', reply_markup=defaults.remove_markup)
        await state.finish()
    else:
        await message.answer('Произошла ошибка. Нажмите /start снова', reply_markup=defaults.remove_markup)
        await state.reset_state()


@dp.message_handler(content_types=['contact'], state=StartState.PHONE)
async def phone_number(message: types.Message, state: FSMContext):
    if message.content_type != 'contact':
        await message.answer('Пожалуйста, отправьте ваш номер для регистрации')
        return

    user, created = await User.get_or_create(user_id=message.from_user.id, phone_number=message.contact.phone_number)
    if user.is_admin:
        result = authorize_user(user)
        if result:
            await message.answer('Вы вошли в систему как администратор')
            await message.answer('Вы успешно зарегестрированы в системе')
            await state.finish()
        else:
            await message.answer('Произошла ошибка. Нажмите /start снова')
            await state.reset_state()
    else:
        await state.set_data({'user': user})
        await message.answer('Вы можете ввести токен администратора или нажать "Пропустить"',
                             reply_markup=defaults.skip_markup)
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
            await message.answer('Вы успешно зарегестрированы в системе')
            await state.finish()
        else:
            await message.answer('Произошла ошибка. Нажмите /start снова')
            await state.reset_state()
    else:
        await message.answer('Токен неправильный. Попробуйте снова или нажмите "Пропустить"')
