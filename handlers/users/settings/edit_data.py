from aiogram import types
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher import FSMContext

from keyboards.inline.create_post import get_create_post_confirm_keyboard , ITEM_CB
from loader import dp, Conn

from keyboards.default.dispatcher import dispatcher, back_button, get_menu_label
from keyboards.inline.user_keyboards import edit_user_role_keyboard
from keyboards.callbacks.user_callback import POST_FILTER_CB

from middlewares import _

from states.state_groups import EditUserDate

from handlers.users.utils import update_state
from utils.db_api.models import File , User
from utils.session.url_dispatcher import REL_URLS


@dp.message_handler(Text(equals=['Вернуться', 'Back']), state=EditUserDate)
async def back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard, path = await back_button(data.get('path'), message.from_user.id)
    await message.answer(text=await get_menu_label(path), reply_markup=keyboard)
    data = await state.get_data()
    if data.get('edit_data'):
        data.pop('edit_data')
    if data.get('user_info'):
        data.pop('user_info')
    await state.finish()
    data['path'] = path
    await state.update_data(**data)


@dp.message_handler(Text(equals=['Сохранить', 'Save']), state=EditUserDate)
async def save_user_data(message: types.Message):
    await message.answer(_('Подтверждаете?'),
                         reply_markup=await get_create_post_confirm_keyboard())
    await EditUserDate.SAVE.set()


@dp.message_handler(Text(equals=['Перейти к имени и фамилии', 'Go to full name']), state=EditUserDate)
async def go_to_full_name(message: types.Message, state: FSMContext):
    await message.answer(_('Введите имя и фамилию через пробел'))
    await EditUserDate.NAME.set()
    data = await state.get_data()
    if 'edit_data' not in data.keys():
        await state.update_data(edit_data={})


@dp.message_handler(Text(equals=['Перейти к электронной почте', 'Go to email']), state=EditUserDate)
async def go_to_email(message: types.Message):
    await message.answer(_('Введите ваш email'))
    await EditUserDate.EMAIL.set()


@dp.message_handler(Text(equals=['Перейти к фото', 'Go to photo']), state=EditUserDate)
async def go_to_email(message: types.Message):
    await message.answer(_('Добавьте фото профиля'))
    await EditUserDate.PHOTO.set()


@dp.message_handler(Text(equals=['Перейти к роли', 'Go to role']), state=EditUserDate)
async def go_to_email(message: types.Message):
    await message.answer(_('Выберите вашу пользовательскую роль'), reply_markup=edit_user_role_keyboard)
    await EditUserDate.ROLE.set()


@dp.message_handler(Text(equals=['Изменить данные', 'Change data']))
async def edit_data(message: types.Message, state: FSMContext):
    await EditUserDate.STARTER.set()
    keyboard, path = await dispatcher('LEVEL_3_EDIT_DATA', message.from_user.id)
    user = await User.get(user_id=message.from_user.id)
    url = f'{REL_URLS["users"]}{user.swipe_id}/'
    resp = await Conn.get(url, user_id=message.from_user.id)
    no_data = _('Не указано')
    info_data = {
        'first_name': resp.get('first_name', no_data),
        'last_name': resp.get('last_name', no_data),
        'email': resp.get('email', no_data),
        'role': resp.get('role_display')
    }
    full_name = (resp.get('first_name') or '') + ' ' + (resp.get('last_name') or '')
    text = _('<b>{name}</b>\n' +
             '<b>Email:</b>: {email}\n' +
             '<b>Роль:</b> {role}').format(name=full_name, email=info_data.get('email'), role=info_data.get('role'))
    await message.answer(_('Текущие данные:\n' + text))
    await message.answer(_('Введите имя и фамилию через пробел.\n' +
                           'Сейчас - <b>{name}</b>').format(name=full_name or no_data), reply_markup=keyboard)
    await EditUserDate.NAME.set()
    await state.update_data(path=path, edit_info={}, user_info=info_data)


@dp.message_handler(state=EditUserDate.NAME)
async def set_full_name(message: types.Message, state: FSMContext):
    answer = message.text

    first_name, *last_name_list = answer.split(' ')
    last_name = ' '.join(last_name_list)
    await update_state(state, first_name, 'first_name', 'edit_data')
    await update_state(state, last_name, 'last_name', 'edit_data')
    data = await state.get_data()
    await message.answer(_('Введите ваш email.\n' +
                           'Сейчас: <b>{email}</b>').format(email=data.get('email', _('Не указано'))))
    await EditUserDate.EMAIL.set()


@dp.message_handler(state=EditUserDate.EMAIL)
async def set_email(message: types.Message, state: FSMContext):
    answer = message.text
    if '@' not in answer or '.' not in answer:
        await message.answer(_('Неверный формат электронной почты'))
        return
    await update_state(state, answer, 'email', 'edit_data')
    data = await state.get_data()
    await message.answer(_('Выбериет вашу пользовательскую роль.\n' +
                           'Сейчас: <b>{role}</b>').format(role=data.get('role')), reply_markup=edit_user_role_keyboard)
    await EditUserDate.ROLE.set()


@dp.callback_query_handler(POST_FILTER_CB.filter(action='edit_role'), state=EditUserDate)
async def edit_role(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    await update_state(state, value, 'role', 'edit_data')
    await call.answer()
    await call.message.answer(_('Добавьте фото профиля'))
    await EditUserDate.PHOTO.set()


@dp.message_handler(state=EditUserDate.PHOTO, content_types=types.ContentType.PHOTO)
async def edit_profile_photo(message: types.Message, state: FSMContext):
    photos = message.photo
    if not photos:
        await message.edit_text(_('Вы не добавили изображение'))
        return
    image = photos[-1].file_id
    await photos[-1].download()
    file, created = await File.get_or_create(file_id=image,
                                             defaults={'filename': photos[-1].file_id})
    await update_state(state, file.file_id, 'photo', 'edit_data')
    await message.answer(_('Подтверждаете?'),
                         reply_markup=await get_create_post_confirm_keyboard())
    await EditUserDate.SAVE.set()


@dp.callback_query_handler(ITEM_CB.filter(action='create_confirm'), state=EditUserDate.SAVE)
async def get_confirm_user(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    if value == 'YES':
        data = await state.get_data()
        user_data = data.get('edit_data')
        photo = await File.get(file_id=user_data.get('photo'))
        image = await call.bot.get_file(photo.file_id)
        user = await User.get(user_id=call.from_user.id)
        with open(image.file_path, 'rb') as rb_image:
            user_data['photo'] = rb_image
            url = f'{REL_URLS["users"]}{user.swipe_id}/'
            resp = await Conn.patch(url, data=user_data, user_id=call.from_user.id)
        if not resp.get('Error'):
            await call.answer(_('Данные обновлены'), show_alert=True)
            data.pop('edit_data')
            await state.finish()
            await state.update_data(**data)
        else:
            await call.answer(_('Произошла ошибка. Попробуйте ещё раз'))
            await call.answer(resp.get('Error'), show_alert=True)
    else:
        await call.answer(_('Вы можете выбрать нужный этап через меню'))
