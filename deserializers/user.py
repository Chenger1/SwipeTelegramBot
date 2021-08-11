from deserializers.base import BaseDeserializer

from middlewares import _


class UserDeserializer(BaseDeserializer):
    async def for_detail(self, data: dict) -> tuple:
        info = _('{name} - {phone}\n Email: {email}').format(
            name = (data['first_name'] or '') + (data['last_name'] or ''),
            phone=data['phone_number'], email=data['email']
        )
        return await self.get_namedtuple(data['pk'], info)

    async def for_list(self, data: dict) -> tuple:
        info = _('{phone}').format(phone=data['phone_number'])
        return await self.get_namedtuple(data['pk'], info)
