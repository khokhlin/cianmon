import os

from peewee import CharField, DateField, IntegerField, TextField
from peewee import Model
from peewee import SqliteDatabase

from .config import CFG_DIR, DATABASE


database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database

    @classmethod
    def get_visible_fields(cls):
        return getattr(cls, "_visible_fields", ())


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
        with database.atomic() as txn:
            cls.insert_many(flat_infos).execute()
            txn.commit()


class PriceHistory(BaseModel):
    flat_id = IntegerField(primary_key=True)
    created_at = DateField()
    price = IntegerField()

    class Meta:
        table_name = "price_history"


def check_database():
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)
    with database:
        database.create_tables([Flat, PriceHistory])
