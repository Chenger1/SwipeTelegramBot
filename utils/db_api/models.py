from tortoise.models import Model
from tortoise import fields


class User(Model):
    user_id = fields.IntField(unique=True)
    token = fields.CharField(max_length=100, unique=True, null=True)
    phone_number = fields.CharField(max_length=30, unique=True)
    is_admin = fields.BooleanField(default=False)
    language = fields.CharField(max_length=5, null=True)


class File(Model):
    filename = fields.CharField(max_length=150)
    file_id = fields.CharField(max_length=255)
    parent_id = fields.IntField()


class AdminToken(Model):
    token = fields.CharField(max_length=100)

    def __str__(self):
        return self.token
