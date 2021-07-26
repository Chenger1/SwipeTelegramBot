from aiohttp import ClientSession

from typing import Dict, Optional

from db import DB


class BaseSessionManager:
    def __init__(self):
        self._session = ClientSession()
        self._database = DB()
        self._WEBHOOK_ENDPOINT = 'http://188.225.43.69:1337'

    async def _prepare_url(self, path: str) -> str:
        """
        Gets path like '/main/resource/' and returns 'http://127.0.0.1:0000/main/resource/'
        :param path: relative
        :return: str - absolute path
        """
        return f'{self._WEBHOOK_ENDPOINT}/{path}'

    async def _get_authorization_header(self, user_id: int = None) -> Optional[Dict[str, str]]:
        """
            If user`s id is given - get token from db
        :param user_id: Telegram user`s id
        :return: Header dict with bearer token or None
        """
        headers = None
        if user_id:
            token = await self._database.get_token(user_id)
            headers = {'Authorization': f'Bearer {token}'}
        return headers

    async def _process_authorization_token(self, user_id: Optional[int], token: Optional[str]):
        """
        If Bearer token has expire time, it will be updated after this is will end.
        So, we have to update our token in db
        :param user_id: Telegram user`s id
        :param token: Bearer Token
        """
        if user_id and token:
            await self._database.update_token(user_id, token)


class SessionManager(BaseSessionManager):
    async def authorize(self, path: str, params: dict = None, user_id: int = None) -> Dict[str, str]:
        """
        Using only for authorizing
        :return Dict: {'phone_number', 'auth'} - 'auth' is a Bearer token
        """
        absolute_url = await self._prepare_url(path)
        async with self._session.get(absolute_url, params=params) as resp:
            data = await resp.json()
            if data.get('auth'):
                await self._database.update_token(user_id, data.get('auth'))
            return await resp.json()

    async def get(self, path: str, data: dict = None, params: dict = None, user_id: int = None) -> Dict[str, str]:
        absolute_url = await self._prepare_url(path)
        headers = await self._get_authorization_header(user_id)
        async with self._session.get(absolute_url, params=params, data=data, headers=headers) as resp:
            await self._process_authorization_token(user_id, resp.headers.get('Authorization'))
            return await resp.json()

    async def patch(self, path: str, data: dict = None, params: dict = None, user_id: int = None) -> Dict[str, str]:
        absolute_url = await self._prepare_url(path)
        headers = await self._get_authorization_header(user_id)
        if headers and headers.get('Authorization'):
            # Only authorized users can change info
            async with self._session.patch(absolute_url, params=params, data=data, headers=headers) as resp:
                await self._process_authorization_token(user_id, resp.headers.get('Authorization'))
                return await resp.json()
        return {'Error': 'Нет id пользователя'}

    async def close(self):
        await self._session.close()
