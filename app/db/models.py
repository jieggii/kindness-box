from enum import Enum

from tortoise import fields
from tortoise.models import Model


class PointCity(str, Enum):
    KOSTOMUKSHA = "Костомукша"
    PETROZAVODSK = "Петрозаводск"
    SEGEZHA = "Сегежа"


class Point(Model):
    class Meta:
        table = "points"

    id = fields.IntField(pk=True)
    city = fields.CharEnumField(enum_type=PointCity, max_length=255)
    address = fields.CharField(max_length=1000)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Point({self.city}, id={self.id})"


class Donator(Model):
    class Meta:
        table = "donators"

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    user_id = fields.IntField()
    org_name = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=255)
    brought_gifts = fields.BooleanField(default=False)
    point = fields.ForeignKeyField("models.Point")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Donator({self.name}, id={self.id})"


class Child(Model):
    class Meta:
        table = "children"

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    age = fields.IntField()
    gift = fields.CharField(max_length=255)

    donator = fields.ForeignKeyField("models.Donator", on_delete=fields.SET_NULL, null=True)
    point = fields.ForeignKeyField("models.Point")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Child({self.name}, id={self.id})"
