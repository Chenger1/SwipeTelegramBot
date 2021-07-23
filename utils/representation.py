from abc import ABC, abstractmethod

from aiogram.utils.markdown import bold, underline, italic

import asyncio

from collections import namedtuple

from typing import Iterable, List, Dict


class BaseRepresentationAgent(ABC):
    @abstractmethod
    async def one_iteration(self, data: Iterable) -> namedtuple:
        pass

    @abstractmethod
    async def one_iteration_many(self, data: Iterable) -> namedtuple:
        pass

    async def async_for_loop(self, coros: Iterable) -> Iterable:
        return await asyncio.gather(*coros)

    async def objects_repr(self, response: List[dict]) -> Iterable[List[str]]:
        coros = [self.one_iteration_many(data) for data in response]
        res = await self.async_for_loop(coros)
        return res


class PostRepresentationAgent(BaseRepresentationAgent):
    async def one_iteration(self, data: Dict) -> namedtuple:
        PostData = namedtuple('PostData', 'pk data')

        post_info = f'{bold("Квартира")}: №{1}, {data["flat_info"]["floor"]}.\n {bold("Город")}: {data["flat_info"]["city"]}\n' + \
                    f'{bold("Площадь")}: {data["flat_info"]["square"]}. {bold("Кухня")}: {data["flat_info"]["kitchen_square"]}\n' + \
                    f'{bold("Документы")}: {data["flat_info"]["foundation_doc"]}.\n {bold("Тип квартиры")}: {data["flat_info"]["type"]}\n' + \
                    f'{bold("Планировка")}: {data["flat_info"]["plan"]}.\n {bold("Территория")}: {data["flat_info"]["territory"]}\n' + \
                    f'{bold("Тип оплаты")}: {data["payment_options"]}.\n {bold("Связь")}: {data["communications"]}\n' + \
                    f'{bold("О предложении")}:\n {data["description"] or "*Описания нет*"}\n {bold("Цена")}: {data["price"]}\n' + \
                    f'{underline("Посмотрели")}: {data["views"]}. {underline("Оценили")}: {data["likes"]}\n'
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


class HouseRepresentationAgent(BaseRepresentationAgent):
    async def one_iteration(self, data: Dict) -> namedtuple:
        HouseData = namedtuple('HouseData', 'pk data')
        info_part = f'{bold(data["name"])}\n{bold("Адрес")}: {data["address"]}\n' + \
                    f'{bold("Тип дома")}: {data["type_display"]}\n' + \
                    f'{bold("Класс дома:")} : {data["house_class_display"]}\n' + \
                    f'{bold("Технология")}: {data["tech_display"]}\n' + \
                    f'{bold("Условия:")}\n' + \
                    f'{bold("Территория")}: {data["territory_display"]}\n' + \
                    f'{bold("Расстояние до моря")}: {data["distance_to_sea"]} м.\n' + \
                    f'{bold("Газопровод")}: {data["gas_display"]}\n' + \
                    f'{bold("Отопление")}: {data["heating_display"]}\n' + \
                    f'{bold("Электричество")}: {data["electricity_display"]}\n' + \
                    f'{bold("Водоснабжение")}: {data["water_supply_display"]}\n' + \
                    f'{bold("Канализация")}: {data["sewerage_display"]}\n'
        if data['description']:
            info_part += f'{bold("Описание")}: {data["description"]}\n'
        if any((data['playground'], data['car_park'], data['shop'],
                data['child_playground'], data['high_speed_elevator'],
                data['security'])):
            info_part += f'{bold("Преимущества:")}\n'
            info_part += f'{italic("* Спортивная площадка")}\n' if data['playground'] else '' + \
                         f'{italic("* Парковка")}\n' if data['car_park'] else '' + \
                         f'{italic("* Рядом магазин")}\n' if data['shop'] else '' + \
                         f'{italic("* Детская площадка")}\n' if data['child_playground'] else '' + \
                         f'{italic("* Скоростной лифт")}\n' if data['high_speed_elevator'] else '' + \
                         f'{italic("* Охрана")}\n' if data['security'] else ''

        house_data = HouseData(data['id'], info_part)
        return house_data

    async def one_iteration_many(self, data: Dict) -> namedtuple:
        HouseData = namedtuple('HouseData', 'pk data')
        info_part = f'{bold(data["name"])}\n{bold("Адрес")}: {data["address"]}\n' + \
                    f'{bold("Тип дома")}: {data["type_display"]}\n' + \
                    f'{bold("Класс дома:")} : {data["house_class_display"]}\n' + \
                    f'{bold("Технология")}: {data["tech_display"]}\n' + \
                    f'{bold("Расстояние до моря")}: {data["distance_to_sea"]} м.'
        house_data = HouseData(data['id'], info_part)
        return house_data
