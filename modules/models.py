from modules.app import db

from peewee import *

import json
import csv


def add_new_row(model, row_data_dict):
    new_user = model(**row_data_dict)

    new_user.save()


def is_there_value_of_field(model, field, value):
    return len(model.select().where(getattr(model, field) == value)) != 0


def export_data_of_query_to_json(query, filename):
    with open(filename, "w") as out:
        json.dump(list(query.dicts()), out)


def export_data_of_query_to_csv(query, filename):
    with open(filename, "w", newline="") as out:
        csv_out = csv.writer(out)

        for row in query.tuples():
            csv_out.writerow(row)


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


class Status_Of_Formular(BaseModel):
    id = AutoField()
    code = CharField(max_length=20, null=False, unique=True)
    name = CharField(max_length=250, null=False, unique=True)


class Formular(BaseModel):
    id = AutoField()
    reader = ForeignKeyField(User, to_field="id")
    book = ForeignKeyField(Book, to_field="id")
    date_of_begin_of_reading = DateField(null=False)
    date_of_end_of_reading = DateField(null=True)
    status = ForeignKeyField(Status_Of_Formular, to_field="id")


db.create_tables([User, Genre, Book, Status_Of_Formular, Formular], safe=True)
