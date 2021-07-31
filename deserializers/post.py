from deserializers.base import BaseDeserializer

from collections import namedtuple

from typing import Dict


class PostDeserializer(BaseDeserializer):
    async def for_detail(self, data: Dict) -> namedtuple:
        post_info = '<b>Квартира</b>: {number}'.format(number=data['flat_info']['number'])
        return await self.get_namedtuple(data['id'], post_info)

    async def for_list(self, data: Dict) -> namedtuple:
        post_info = '<b>Квартира</b>: {number}'.format(number=data['flat_info']['number'])
        return await self.get_namedtuple(data['id'], post_info)
