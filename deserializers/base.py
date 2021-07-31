from abc import ABC, abstractmethod

import asyncio

from collections import namedtuple

from typing import Iterable, List, Dict


class BaseDeserializer(ABC):
    @abstractmethod
    async def for_detail(self, data: Dict) -> namedtuple:
        pass

    @abstractmethod
    async def for_list(self, data: Dict) -> namedtuple:
        pass

    async def async_for_loop(self, coros: Iterable) -> Iterable:
        return await asyncio.gather(*coros)

    async def make_list(self, response: Dict) -> Iterable[List[str]]:
        coros = [self.for_list(data) for data in response.get('results', [])]
        res = await self.async_for_loop(coros)
        return res

    async def get_namedtuple(self, obj_id: int, data: str) -> namedtuple:
        Inst = namedtuple('Inst', 'pk data')
        return Inst(obj_id, data)
