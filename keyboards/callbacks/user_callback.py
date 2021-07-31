from aiogram.utils.callback_data import CallbackData

LANG_CB = CallbackData('lang', 'action', 'lang')

DETAIL_CB = CallbackData('detail', 'action', 'pk')

LIST_CB = CallbackData('list', 'action', 'page', sep=';')


def get_detail_callback(action: str, pk: int) -> str:
    return DETAIL_CB.new(action=action, pk=pk)


def get_list_callback(action: str, page: str) -> str:
    return LIST_CB.new(
        action=action,
        page=page
    )
