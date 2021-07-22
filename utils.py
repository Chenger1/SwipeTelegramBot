from main import WEBHOOK_ENDPOINT


def prepare_url(path: str) -> str:
    """
    Gets path like '/main/resource/' and returns 'http://127.0.0.1:0000/main/resource/'
    :param path: relative
    :return: str - absolute path
    """
    return f'{WEBHOOK_ENDPOINT}/{path}'
