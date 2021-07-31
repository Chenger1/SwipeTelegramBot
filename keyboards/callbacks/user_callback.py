from aiogram.utils.callback_data import CallbackData

LANG_CB = CallbackData('lang', 'action', 'lang')

DETAIL_WITH_PAGE_CB = CallbackData('detail', 'action', 'pk', 'page', sep=';')
DETAIL_CB = CallbackData('detail', 'action', 'pk')
COMPLAINT_CB = CallbackData('complaint', 'action', 'pk', 'type')
LIKE_DISLIKE_CB = CallbackData('detail', 'action', 'pk', 'type', 'page')

LIST_CB = CallbackData('list', 'action', 'page', sep=';')


def get_detail_callback_with_page(action: str, pk: int, page: str) -> str:
    return DETAIL_WITH_PAGE_CB.new(action=action, pk=pk, page=page)


def get_detail_callback(action: str, pk: int) -> str:
    return DETAIL_CB.new(action=action, pk=pk)


def get_list_callback(action: str, page: str) -> str:
    return LIST_CB.new(
        action=action,
        page=page
    )
