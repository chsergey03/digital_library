from modules.app import db

from peewee import *


def add_new_row(model, row_data_dict):
    new_user = model(**row_data_dict)

    new_user.save()


def is_there_value_of_field(model, field, value):
    return len(model.select().where(getattr(model, field) == value)) != 0


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    login = CharField(max_length=250, null=False, unique=True)
    email = CharField(max_length=250, null=True, unique=True)
    password_hash = CharField(max_length=250, null=False, unique=False)

    @staticmethod
    def add_new(attributes):
        new_user = User(*attributes)

        new_user.save()


class Genre(BaseModel):
    id = AutoField()
    code = CharField(max_length=20, null=False, unique=True)
    name = CharField(max_length=250, null=False, unique=True)


class Book(BaseModel):
    id = AutoField()
    title = CharField(max_length=250, null=False)
    author = CharField(max_length=250, null=False)
    publisher = CharField(max_length=250, null=False)
    release_year = IntegerField(null=False)
    genre = ForeignKeyField(Genre, to_field="id")


db.create_tables([User, Genre, Book], safe=True)
