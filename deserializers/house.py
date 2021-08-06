from deserializers.base import BaseDeserializer

from typing import Tuple, Dict

from middlewares import _


class HouseDeserializer(BaseDeserializer):
    async def for_list(self, data: Dict) -> Tuple:
        info = _('<b>{name}</b>\n' +
                 '<i>{address}.{city}</i>\n').format(name=data.get('name'),
                                                     address=data.get('address'),
                                                     city=data.get('city'))
        return await self.get_namedtuple(data['id'], info)

    async def for_detail(self, data: Dict) -> Tuple:
        info = _('<b>{name}</b>\n' +
                 '<i>{address}.{city}</i>\n' +
                 '<b>Предназначение:</b> {role}\n' +
                 '<b>Тип:</b> {type}\n' +
                 '<b>Класс:</b> {klass}\n' +
                 '<b>Технология:</b> {tech}\n' +
                 '<b>Территория:</b> {terr}\n' +
                 '<b>Расстояние до моря:</b> {sea}\n' +
                 '<b>Высота потолков:</b> {height}\n' +
                 '<b>Отопление:</b> {heating}\n' +
                 '<b>Газопровод:</b> {gas}\n' +
                 '<b>Электричество:</b> {electricity}\n' +
                 '<b>Канализация:</b> {sewerage}\n' +
                 '<b>Водоснабжение:</b> {water}\n' +
                 '----------------------------------------\n' +
                 '{description}\n').format(name=data['name'], address=data['address'],
                                           city=data.get('city'), role=data.get('role_display'),
                                           type=data.get('type_display'), klass=data.get('house_class_display'),
                                           tech=data.get('tech_display'), terr=data.get('territory_display'),
                                           sea=data.get('distance_to_sea'), height=data.get('ceiling_height')
                                                                                   or _('Не указано'),
                                           gas=data.get('gas_display'), heating=data.get('heating_display'),
                                           electricity=data.get('electricity_display'),
                                           sewerage=data.get('sewerage_display'), water=data.get('water_supply_display'),
                                           description=data.get('description') or _('Нет описания'))
        return await self.get_namedtuple(data['id'], info)
