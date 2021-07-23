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

        post_info = f'Квартира: №{1}, {data["flat_info"]["floor"]}. \n Город: {data["flat_info"]["city"]}\n' + \
                    f'Площадь: {data["flat_info"]["square"]}. Кухня: {data["flat_info"]["kitchen_square"]} \n' + \
                    f'Документы: {data["flat_info"]["foundation_doc"]}. Тип квартиры: {data["flat_info"]["type"]} \n' + \
                    f'Планировка: {data["flat_info"]["plan"]}. Территория: {data["flat_info"]["territory"]} \n' + \
                    f'Тип оплаты: {data["payment_options"]}. Связь: {data["communications"]} \n' + \
                    f'О предложении: \n {data["description"] or "*Описания нет*"} \n Цена: {data["price"]} \n' + \
                    f'Посмотрели: {data["views"]}. Оценили: {data["likes"]} \n'
        post_data = PostData(data['id'], post_info)
        return post_data

    async def one_iteration_many(self, data: Dict) -> namedtuple:
        PostData = namedtuple('PostData', 'pk data')

        post_info = f'Квартира: №{1}, {data["flat_info"]["floor"]}. \n Город: {data["flat_info"]["city"]}\n' + \
                    f'Площадь: {data["flat_info"]["square"]}. ' + \
                    f'Тип оплаты: {data["payment_options"]}. Связь: {data["communications"]} \n' + \
                    f'О предложении: \n {data["description"] or "*Описания нет*"} \n Цена: {data["price"]} \n' + \
                    f'Посмотрели: {data["views"]}. Оценили: {data["likes"]} \n'
        post_data = PostData(data['id'], post_info)
        return post_data

    async def posts_repr(self, response: List[dict]) -> Iterable[List[str]]:
        coros = [self.one_iteration_many(data) for data in response]
        res = await self.async_for_loop(coros)
        return res
