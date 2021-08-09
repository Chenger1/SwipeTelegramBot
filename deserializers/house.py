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
                 '<b>Количество корпусов:</b> {build}\n' +
                 '<b>Количество секций:</b> {section}\n' +
                 '<b>Количество этажей:</b> {floor_count}\n' +
                 '<b>Количество квартир:</b> {flat}\n' +
                 '----------------------------------------\n' +
                 '{description}\n').format(name=data['name'], address=data['address'],
                                           city=data.get('city'), role=data.get('role_display'),
                                           type=data.get('type_display'), klass=data.get('house_class_display'),
                                           tech=data.get('tech_display'), terr=data.get('territory_display'),
                                           sea=data.get('distance_to_sea'), height=data.get('ceiling_height')
                                                                                   or _('Не указано'),
                                           gas=data.get('gas_display'), heating=data.get('heating_display'),
                                           electricity=data.get('electricity_display'),
                                           sewerage=data.get('sewerage_display'),
                                           water=data.get('water_supply_display'),
                                           description=data.get('description') or _('Нет описания'),
                                           build=data.get('building_count'),
                                           section=data.get('section_count'),
                                           floor_count=data.get('floor_count'),
                                           flat=data.get('flat_count')
                                           )
        return await self.get_namedtuple(data['id'], info)


class FlatDeserializer(BaseDeserializer):
    async def for_list(self, data: Dict) -> Tuple:
        info = _('<b>№:</b> {number}\n' +
                 '<b>Площадь:</b> {square}\n' +
                 '<b>Количество комнат:</b> {rooms}\n' +
                 '<b>Цена:</b> {price}\n' +
                 '<b>Состояние:</b> {state}\n' +
                 '<b>Этаж:</b> {floor}\n').format(number=data.get('number'),
                                                  square=data.get('square'),
                                                  rooms=data.get('number_of_rooms'),
                                                  price=data.get('price'),
                                                  state=data.get('state_display'),
                                                  floor=data.get('floor_display'))
        return await self.get_namedtuple(data['id'], info)

    async def for_detail(self, data: Dict) -> Tuple:
        info = _('<b>№:</b> {number}\n' +
                 '<b>Площадь:</b> {square}\n' +
                 '<b>Количество комнат:</b> {rooms}\n' +
                 '<b>Цена:</b> {price}\n' +
                 '<b>Состояние:</b> {state}\n' +
                 '<b>Этаж:</b> {floor}\n' +
                 '<b>Тип:</b> {type}\n' +
                 '<b>Планировка:</b> {plan}\n' +
                 '<b>Балкон/Лоджия:</b> {balcony}\n' +
                 '<b>Документ:</b> {doc}\n'
                 ).format(number=data.get('number'),
                          square=data.get('square'),
                          rooms=data.get('number_of_rooms'),
                          price=data.get('price'),
                          state=data.get('state_display'),
                          floor=data.get('floor_display'),
                          type=data.get('type_display'),
                          plan=data.get('plan_display'),
                          balcony=data.get('balcony_display'),
                          doc=data.get('doc_display'),
                          )
        return await self.get_namedtuple(data['id'], info)
