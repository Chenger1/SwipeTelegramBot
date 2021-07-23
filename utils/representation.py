from abc import ABC, abstractmethod

from aiogram.utils.markdown import bold, underline

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

        post_info = f'{bold("Квартира")}: №{1}, {data["flat_info"]["floor"]}. \n {bold("Город")}: {data["flat_info"]["city"]}\n' + \
                    f'{bold("Площадь")}: {data["flat_info"]["square"]}. {bold("Кухня")}: {data["flat_info"]["kitchen_square"]} \n' + \
                    f'{bold("Документы")}: {data["flat_info"]["foundation_doc"]}. \n {bold("Тип квартиры")}: {data["flat_info"]["type"]} \n' + \
                    f'{bold("Планировка")}: {data["flat_info"]["plan"]}. \n {bold("Территория")}: {data["flat_info"]["territory"]} \n' + \
                    f'{bold("Тип оплаты")}: {data["payment_options"]}. \n {bold("Связь")}: {data["communications"]} \n' + \
                    f'{bold("О предложении")}: \n {data["description"] or "*Описания нет*"} \n {bold("Цена")}: {data["price"]} \n' + \
                    f'{underline("Посмотрели")}: {data["views"]}. {underline("Оценили")}: {data["likes"]} \n'
        post_data = PostData(data['id'], post_info)
        return post_data

    async def one_iteration_many(self, data: Dict) -> namedtuple:
        PostData = namedtuple('PostData', 'pk data')

        post_info = f'{bold("Квартира")}: №{1}, {data["flat_info"]["floor"]}. \n {bold("Город")}: {data["flat_info"]["city"]}\n' + \
                    f'{bold("Площадь")}: {data["flat_info"]["square"]}. \n' + \
                    f'{bold("Тип оплаты")}: {data["payment_options"]}.\n {bold("Связь")}: {data["communications"]} \n' + \
                    f'{bold("О предложении")}: \n {data["description"] or "*Описания нет*"} \n {bold("Цена")}: {data["price"]} \n' + \
                    f'{underline("Посмотрели")}: {data["views"]}. {underline("Оценили")}: {data["likes"]} \n'
        post_data = PostData(data['id'], post_info)
        return post_data

    async def posts_repr(self, response: List[dict]) -> Iterable[List[str]]:
        coros = [self.one_iteration_many(data) for data in response]
        res = await self.async_for_loop(coros)
        return res
