import os
import datetime
import logging
from collections import namedtuple

from peewee import CharField, DateTimeField, IntegerField
from peewee import TextField, ForeignKeyField
from peewee import Model
from peewee import SqliteDatabase
from playhouse.shortcuts import model_to_dict

from .config import CFG_DIR, DATABASE


database = SqliteDatabase(DATABASE)
LOGGER = logging.getLogger(__name__)


class BaseModel(Model):
    class Meta:
        database = database

    @classmethod
    def get_visible_fields(cls):
        return getattr(cls, "_visible_fields", ())

    def to_dict(self):
        return {
            key: value for key, value
            in model_to_dict(self).items()
            if key in self.get_visible_fields()
        }


class Flat(BaseModel):
    flat_id = IntegerField(primary_key=True)
    title = CharField()
    square_total = IntegerField()
    square_live = IntegerField()
    square_kitchen = IntegerField()
    floor = IntegerField()
    floors = IntegerField()
    build_year = IntegerField()
    description = TextField()
    geo = CharField()
    price = IntegerField()

    _visible_fields = ["flat_id", "title", "square_total", "square_live", "price"]

    class Meta:
        table_name = "flats"

    @classmethod
    def get_flats(cls, ids=None):
        query = cls.select()
        if ids:
            query = query.where(cls.flat_id << ids)
        return query

    @classmethod
    def save_flats(cls, flat_infos):
        prices = []
        for newflat in flat_infos:
            flat, created = cls.get_or_create(flat_id=newflat["flat_id"], defaults=newflat)
            if not created:
                for key, value in newflat.items():
                    setattr(flat, key, value)
            flat.save()
            LOGGER.debug("%s flat was %s", newflat["flat_id"], "created" if created else "updated")
            FlatPrice.update_price(flat_id=flat.flat_id, price=flat.price)


class FlatPrice(BaseModel):
    flat_price_id = IntegerField(primary_key=True)
    flat_id = ForeignKeyField(Flat, backref='prices')
    created_at = DateTimeField(default=datetime.datetime.now)
    price = IntegerField()

    class Meta:
        table_name = "flat_prices"

    @classmethod
    def update_price(cls, flat_id, price):
        cls.create(flat_id=flat_id, price=price)

    @classmethod
    def update_prices(cls, new_prices):
        with database.atomic() as txn:
            cls.insert_many(new_prices).execute()
            txn.commit()


def check_database():
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)
    with database:
        database.create_tables([Flat, FlatPrice])
