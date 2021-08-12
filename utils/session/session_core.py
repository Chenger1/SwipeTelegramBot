from aiohttp import ClientSession

from typing import Dict, Optional

from utils.db_api.models import User

import re


class BaseSessionManager:
    available_file_types = ('image/png', 'image/jpeg', 'image/jpg', 'application/msword',
                            'application/pdf', 'application/vnd.ms-powerpoint', 'application/vnd.ms-excel',
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def __init__(self):
        self._session = ClientSession()
        self._WEBHOOK_ENDPOINT = 'http://188.225.43.69:1337'
        self._wrong_hook_pattern = re.compile('http:\/\/[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}\/')
        # wrong pattern is 'http://188.225.43.69' without port

    async def _prepare_url(self, path: str) -> str:
        """
        Gets path like '/main/resource/' and returns 'http://127.0.0.1:0000/main/resource/'
        :param path: relative
        :return: str - absolute path
        """
        if self._wrong_hook_pattern.findall(path):
            path = self._wrong_hook_pattern.split(path)[-1]
        return f'{self._WEBHOOK_ENDPOINT}/{path}'

    async def _get_authorization_header(self, user_id: int = None) -> Optional[Dict[str, str]]:
        """
            If user`s id is given - get token from db
        :param user_id: Telegram user`s id
        :return: Header dict with bearer token or None
        """
        headers = None
        if user_id:
            user = await User.get(user_id=user_id)
            headers = {'Authorization': f'Bearer {user.token}',
                       'Accept-Language': user.language}
        return headers

    async def _process_authorization_token(self, user_id: Optional[int], token: Optional[str]):
        """
        If Bearer token has expire time, it will be updated after this is will end.
        So, we have to update our token in db
        :param user_id: Telegram user`s id
        :param token: Bearer Token
        """
        if user_id and token:
            user = await User.get(user_id=user_id)
            user.token = token
            await user.save()
