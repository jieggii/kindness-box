from enum import Enum

from tortoise import fields
from tortoise.models import Model


class PointCity(str, Enum):
    KOSTOMUKSHA = "Костомукша"
    PETROZAVODSK = "Петрозаводск"
    MUEZERKA = "Муезерка"


class Point(Model):
    class Meta:
        table = "points"

    point_id = fields.IntField(pk=True)
    locality = fields.CharEnumField(enum_type=PointCity, max_length=255)
    address = fields.CharField(max_length=1000)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Point({self.point_id}, {self.locality})"


class Donator(Model):
    class Meta:
        table = "donators"

    donator_id = fields.IntField(pk=True)
    vk_user_id = fields.IntField()
    name = fields.CharField(max_length=255)
    org_name = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=255)
    brought_gifts = fields.BooleanField(default=False)
    point = fields.ForeignKeyField("models.Point", related_name="point_id")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Donator({self.donator_id}, {self.name})"


class Person(Model):
    class Meta:
        table = "persons"

    person_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    age = fields.IntField()
    gift = fields.CharField(max_length=255)

    donator = fields.ForeignKeyField("models.Donator", related_name="donator_id", on_delete=fields.SET_NULL, null=True)
    point = fields.ForeignKeyField("models.Point", related_name="point_id")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Person({self.person_id}, {self.name})"
