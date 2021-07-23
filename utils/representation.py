from abc import ABC, abstractmethod

import asyncio

from collections import namedtuple

from typing import Iterable, List, Dict


class BaseRepresentationAgent(ABC):
    @abstractmethod
    async def one_iteration(self, data: Iterable) -> namedtuple:
        pass

    async def async_for_loop(self, coros: Iterable) -> Iterable:
        return await asyncio.gather(*coros)


class PostRepresentationAgent(BaseRepresentationAgent):
    async def one_iteration(self, data: Dict) -> namedtuple:
        PostData = namedtuple('PostData', 'pk data')

        flat1 = f'Квартира: №{1}, {data["flat_info"]["floor"]}. \n Город: {data["flat_info"]["city"]}\n'
        flat2 = f'Площадь: {data["flat_info"]["square"]}. Кухня: {data["flat_info"]["kitchen_square"]} \n'
        flat3 = f'Документы: {data["flat_info"]["foundation_doc"]}. Тип квартиры: {data["flat_info"]["type"]} \n'
        flat4 = f'Планировка: {data["flat_info"]["plan"]}. Территория: {data["flat_info"]["territory"]} \n'
        flat_info = flat1+flat2+flat3+flat4
        post1 = f'Тип оплаты: {data["payment_options"]}. Связь: {data["communications"]} \n'
        post2 = f'О предложении: \n {data["description"] or "*Описания нет*"} \n Цена: {data["price"]} \n'
        post3 = f'Посмотрели: {data["views"]}. Оценили: {data["likes"]} \n'
        post_info = post1 + post2 + post3
        post_data = PostData(data['id'], flat_info+post_info)
        return post_data

    async def posts_repr(self, response: List[dict]) -> Iterable[List[str]]:
        coros = [self.one_iteration(data) for data in response]
        res = await self.async_for_loop(coros)
        return res
