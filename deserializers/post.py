from deserializers.base import BaseDeserializer

from collections import namedtuple

from typing import Dict

from middlewares import _


class PostDeserializer(BaseDeserializer):
    async def for_detail(self, data: Dict) -> namedtuple:
        post_info = _('<b>Квартира:</b> {number}\n').format(number=data['flat_info']['number']) + \
                    _('<b>Город:</b> {city}\n').format(city=data['flat_info']['city']) + \
                    _('<b>Документы:</b> {doc}\n').format(doc=data['flat_info']['foundation_doc_display']) + \
                    _('<b>Планировка:</b> {plan}\n').format(plan=data['flat_info']['plan']) + \
                    _('<b>Кухня:</b> {kitchen}').format(kitchen=data['flat_info']['kitchen_square']) + \
                    _('<b>Тип квартиры:</b> {type}\n').format(type=data['flat_info']['type']) + \
                    _('<b>Территория:</b> {terr}').format(terr=data['flat_info']['terr']) + \
                    _('<b>Тип оплаты:</b> {pay}\n').format(pay=data['payment_options_display']) + \
                    _('<b>О предложении:</b> {desc}\n').format(desc=data['description']) + \
                    _('<b>Цена:</b> {price}').format(price=data['price']) + \
                    _('<i>Посмотрели:</i> {views}\n').format(views=data['views']) + \
                    _('<i>Рейтинг:</i> {rate}\n').format(rate=data['likes'])
        return await self.get_namedtuple(data['id'], post_info)

    async def for_list(self, data: Dict) -> namedtuple:
        post_info = _('<b>Город:</b> {about}\n').format(about=data.get('flat_info')['city']) + \
                    _('<b>Площадь</b> {square} | ').format(square=data.get('flat_info')['square']) + \
                    _('<b>Связь:</b> {comm}\n').format(comm=data['communications_display']) + \
                    _('<b>Цена:</b> {price}грн.').format(price=data.get('price'))
        return await self.get_namedtuple(data['id'], post_info)
