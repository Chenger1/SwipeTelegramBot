from aiohttp.client_exceptions import ContentTypeError

from typing import Dict, Tuple

from utils.session.session_core import BaseSessionManager


class SessionManager(BaseSessionManager):
    async def authorize(self, path: str, params: dict = None, user_id: int = None) -> Dict[str, str]:
        """
        Using only for authorizing
        :return Dict: {'phone_number', 'auth'} - 'auth' is a Bearer token
        """
        absolute_url = await self._prepare_url(path, user_id)
        async with self._session.get(absolute_url, params=params) as resp:
            data = await resp.json()
            return data

    async def get(self, path: str, data: dict = None, params: dict = None, user_id: int = None) -> Dict[str, str]:
        absolute_url = await self._prepare_url(path, user_id)
        headers = await self._get_authorization_header(user_id)
        async with self._session.get(absolute_url, params=params, data=data, headers=headers) as resp:
            await self._process_authorization_token(user_id, resp.headers.get('Authorization'))
            if resp.content_type in self.available_file_types:
                return {'filename': path.split('/')[-1], 'file': await resp.read(),
                        'file_type': resp.content_type}
            else:
                try:
                    data = await resp.json()
                except ContentTypeError:
                    return {'Error': f'Status: {resp.status}'}
            return data

    async def patch(self, path: str, data: dict = None, params: dict = None, user_id: int = None) -> Dict[str, str]:
        absolute_url = await self._prepare_url(path, user_id)
        headers = await self._get_authorization_header(user_id)
        if headers and headers.get('Authorization'):
            # Only authorized users can change info
            async with self._session.patch(absolute_url, params=params, data=data, headers=headers) as resp:
                await self._process_authorization_token(user_id, resp.headers.get('Authorization'))
                try:
                    data = await resp.json()
                except ContentTypeError:
                    return {'Error': f'Status: {resp.status}'}
                return data
        return {'Error': 'Нет id пользователя'}

    async def post(self, path: str, data: dict = None, params: dict = None, user_id: int = None) -> Tuple[Dict[str, str], int]:
        absolute_url = await self._prepare_url(path, user_id)
        headers = await self._get_authorization_header(user_id)
        if headers and headers.get('Authorization'):
            # Only authorized users can change info
            async with self._session.post(absolute_url, params=params, data=data, headers=headers) as resp:
                await self._process_authorization_token(user_id, resp.headers.get('Authorization'))
                try:
                    return await resp.json(), resp.status
                except ContentTypeError:
                    return {'Error': f'Status: {resp.status}'}, resp.status
        return {'Error': 'Нет id пользователя'}, 400

    async def delete(self, path: str, user_id: int = None) -> Tuple[Dict[str, str], int]:
        absolute_url = await self._prepare_url(path, user_id)
        headers = await self._get_authorization_header(user_id)
        if headers and headers.get('Authorization'):
            async with self._session.delete(absolute_url, headers=headers) as resp:
                await self._process_authorization_token(user_id, resp.headers.get('Authorization'))
                return {}, resp.status
        return {'Error': 'Нет id пользователя'}, 400

    async def close(self):
        await self._session.close()
