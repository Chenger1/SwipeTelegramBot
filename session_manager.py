from aiohttp import ClientSession

from typing import Dict


class BaseSessionManager:
    def __init__(self):
        self._session = ClientSession()
        self._WEBHOOK_ENDPOINT = 'http://188.225.43.69:1337'

    async def _prepare_url(self, path: str) -> str:
        """
        Gets path like '/main/resource/' and returns 'http://127.0.0.1:0000/main/resource/'
        :param path: relative
        :return: str - absolute path
        """
        return f'{self._WEBHOOK_ENDPOINT}/{path}'


class SessionManager(BaseSessionManager):
    async def get(self, path: str, data: dict = None, params: dict = None) -> Dict[str, str]:
        absolute_url = await self._prepare_url(path)
        async with self._session.get(absolute_url, params=params, data=data) as resp:
            return await resp.json()

    async def close(self):
        await self._session.close()
