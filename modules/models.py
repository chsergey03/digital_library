from modules.app import db

from peewee import *
from flask import request

import json
import csv


def add_new_row(model, row_data_dict):
    new_row = model(**row_data_dict)
    new_row.save()

    return new_row


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


def get_role_code():
    login = request.cookies.get("login")
    user_id = User.get(User.login == login).id

    role_code = (Role
                 .get(Role.id ==
                      Role_Of_User.get(Role_Of_User.user == user_id).role)
                 .code)

    return role_code


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    login = CharField(max_length=250, null=False, unique=True)
    email = CharField(max_length=250, null=True, unique=True)
    password_hash = CharField(max_length=250, null=False, unique=False)


class Role(BaseModel):
    id = AutoField()
    code = CharField(max_length=20, null=False, unique=True)
    name = CharField(max_length=250, null=False, unique=True)


class Role_Of_User(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, to_field="id")
    role = ForeignKeyField(Role, to_field="id")


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


db.create_tables([User, Role, Role_Of_User,
                  Genre, Book, Status_Of_Formular, Formular], safe=True)

if not User.select().count():
    file = open("data/admin.txt")

    add_new_row(User,
                {"login": file.readline()[:-1],
                 "email": file.readline()[:-1],
                 "password_hash": file.readline()})

if not Role.select().count():
    add_new_row(Role, {"code": "ADMIN", "name": "Администратор"})
    add_new_row(Role, {"code": "LIBRARIAN", "name": "Библиотекарь"})
    add_new_row(Role, {"code": "READER", "name": "Читатель"})

if not Role_Of_User.select().count():
    add_new_row(Role_Of_User, {"user": 1, "role": 1})
