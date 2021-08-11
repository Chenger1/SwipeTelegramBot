from deserializers.base import BaseDeserializer

from collections import namedtuple

from typing import Dict

from middlewares import _


class PostDeserializer(BaseDeserializer):
    async def for_detail(self, data: Dict) -> namedtuple:
        post_info = _('<b>Квартира:</b> №{number}\n').format(number=data['flat_info']['number']) + \
                    _('<b>Город:</b> {city}\n').format(city=data['flat_info']['city']) + \
                    _('<b>Документы:</b> {doc}\n').format(doc=data['flat_info']['foundation_doc']) + \
                    _('<b>Планировка:</b> {plan}\n').format(plan=data['flat_info']['plan']) + \
                    _('<b>Кухня:</b> {kitchen}\n').format(kitchen=data['flat_info']['kitchen_square']) + \
                    _('<b>Тип квартиры:</b> {type}\n').format(type=data['flat_info']['type']) + \
                    _('<b>Территория:</b> {terr}\n').format(terr=data['flat_info']['territory']) + \
                    _('<b>Тип оплаты:</b> {pay}\n').format(pay=data['payment_options_display']) + \
                    _('<b>О предложении:</b> {desc}\n').format(desc=data['description'] or 'Не указано') + \
                    _('<b>Цена:</b> {price}\n').format(price=data['price']) + \
                    _('<i>Посмотрели:</i> {views}\n').format(views=data['views']) + \
                    _('<i>Рейтинг:</i> {rate}\n').format(rate=data['likes'])
        return await self.get_namedtuple(data['id'], post_info)

    async def for_list(self, data: Dict) -> namedtuple:
        post_info = _('<b>Город:</b> {about}\n').format(about=data.get('flat_info')['city']) + \
                    _('<b>Площадь</b> {square} | ').format(square=data.get('flat_info')['square']) + \
                    _('<b>Связь:</b> {comm}\n').format(comm=data['communications_display']) + \
                    _('<b>Цена:</b> {price} грн.').format(price=data.get('price'))
        return await self.get_namedtuple(data['id'], post_info)


class PostFilterDeserializer(BaseDeserializer):
    _no_data = _('Не указано')

    async def for_detail(self, data: Dict) -> namedtuple:
        info = _('<b>{name}</b>\n' +
                 '<b>Цена:</b> {price__gte}:{price__lte}\n' +
                 '<b>Площадь:</b> {square__gte}:{square__lte}\n' +
                 '<b>Город:</b> {city}\n' +
                 '<b>Состояние:</b> {state}\n' +
                 '<b>Планировка:</b> {plan}\n' +
                 '<b>Территория:</b> {terr}\n').format(name=data.get('name'),
                                                       price__gte=data.get('price__gte', self._no_data),
                                                       price__lte=data.get('price__lte', self._no_data),
                                                       square__gte=data.get('flat__square__gte', self._no_data),
                                                       square__lte=data.get('flat__square__lte', self._no_data),
                                                       city=data.get('house__city', self._no_data),
                                                       state=data.get('flat__state', self._no_data),
                                                       plan=data.get('flat__plan', self._no_data),
                                                       terr=data.get('house__territory', self._no_data))
        return await self.get_namedtuple(data['saved_filter_pk'], info)

    async def for_list(self, data: Dict) -> namedtuple:
        info = _('<b>{name}</b>').format(name=data.get('name'))
        return await self.get_namedtuple(data['saved_filter_pk'], info)


class HouseForCreatePost(BaseDeserializer):
    async def for_detail(self, data: Dict) -> namedtuple:
        info = _('<b>{name}</b>\n' +
                 '<b>{address}</b>\n' +
                 '<b>{city}</b>',
                 '<b>Тип</b>: {type}').format(name=data.get('name'),
                                              address=data.get('address'),
                                              city=data.get('city'),
                                              type=data.get('type_display'))
        return await self.get_namedtuple(data['id'], info)

    async def for_list(self, data: Dict) -> namedtuple:
        info = _('<b>{name}</b>\n' +
                 '<b>{address}</b>\n' +
                 '<b>{city}</b>').format(name=data.get('name'),
                                         address=data.get('address'),
                                         city=data.get('city'))
        return await self.get_namedtuple(data['id'], info)


class FlatForCreatePost(BaseDeserializer):
    async def for_detail(self, data: Dict) -> namedtuple:
        owned = data.get('owned')
        booked = data.get('booked')
        status = True if owned or booked else False
        info = _('<b>Квартира </>№ {number}\n' +
                 '<b>Площадь:</b> {square} м2\n' +
                 '<b>Цена:</b> {price}\n' +
                 '<b>Кол-во комнат:</b> {rooms}\n' +
                 '<b>Свободна:</b> {free}\n').format(number=data.get('number'),
                                                     square=data.get('square'),
                                                     price=data.get('price'),
                                                     rooms=data.get('number_of_rooms'),
                                                     free=_('Нет') if status else _('Да'))
        return await self.get_namedtuple(data['id'], info)

    async def for_list(self, data: Dict) -> namedtuple:
        owned = data.get('owned')
        booked = data.get('booked')
        status = True if owned or booked else False
        info = _('<b>Квартира </>№ {number}\n' +
                 '<b>Свободна:</b> {free}').format(number=data.get('number'),
                                                   free=_('Нет') if status else _('Да'))
        return await self.get_namedtuple(data['id'], info)


class ComplaintDeserializer(BaseDeserializer):
    async def for_detail(self, data: Dict) -> namedtuple:
        rejected = data['post_display']['rejected']
        message = data['post_display']['rejected_message'] or _('Нет')
        info = _('{house}. {flat}\n' +
                 '<b>Цена: </b>{price}\n' +
                 '<b>Просмотры: </b>{views}\n' +
                 '<b>Заблокирован:</b>{rejected}\n' +
                 '<b>Причина: </b> {message}\n' +
                 'Причина жалобы: {type}\n').format(house=data['post_display']['house'],
                                                  flat=data['post_display']['flat_floor'],
                                                  views=data['post_display']['views'],
                                                  price=data['post_display']['price'],
                                                  rejected=_('Да') if rejected else _('Нет'),
                                                  message=message,
                                                  type=data['type_display'])
        return await self.get_namedtuple(data['id'], info)

    async def for_list(self, data: Dict) -> namedtuple:
        info = _('{house}. {flat}\n' +
                 'Причина жалобы: {type}\n').format(house=data['post_display']['house'],
                                                  flat=data['post_display']['flat_floor'],
                                                  type=data['type_display'])
        return await self.get_namedtuple(data['id'], info)
