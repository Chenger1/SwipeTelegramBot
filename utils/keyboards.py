from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


DETAIL_CB = CallbackData('detail', 'action', 'pk')


def get_detail_keyboard(pk: int, title: str, action: str) -> InlineKeyboardMarkup:
    """ Generate one button which includes primary key of object """
    inline_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(title,
                             callback_data=DETAIL_CB.new(action=action,
                                                         pk=pk))
    )
    return inline_markup
