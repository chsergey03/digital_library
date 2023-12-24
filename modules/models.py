from modules.app import db

from peewee import *
from flask import request

import json
import csv


def add_new_row(model, row_data_dict):
    new_row = model(**row_data_dict)
    new_row.save()


def delete_row_by_id(row_id, model):
    row_to_delete = (model
                     .get(model.id == row_id))

    row_to_delete.delete_instance()


def try_to_delete_row_through_form(form_name, model):
    row_id = request.form.get(form_name)

    if request.method == "POST" and row_id:
        delete_row_by_id(row_id, model)


def update_row(model, row_id, row_new_data_dict):
    new_row = (model
               .update(**row_new_data_dict)
               .where(model.id == row_id))

    new_row.execute()


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


def get_login_from_cookies():
    return request.cookies.get("login")


def get_role_code():
    user_role = (User
                 .get(User.login == get_login_from_cookies())
                 .role)

    role_code = (Role
                 .get(Role.id == user_role)
                 .code)

    return role_code


def get_user_by_login():
    user = User.get(User.login == get_login_from_cookies())

    return user


class BaseModel(Model):
    class Meta:
        database = db


class Role(BaseModel):
    id = AutoField()
    code = CharField(max_length=20, null=False, unique=True)
    name = CharField(max_length=250, null=False, unique=True)


class User(BaseModel):
    id = AutoField()
    login = CharField(max_length=250, null=False, unique=True)
    email = CharField(max_length=250, null=True, unique=True)
    password_hash = CharField(max_length=250, null=False, unique=False)
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


class Formular(BaseModel):
    id = AutoField()
    reader = ForeignKeyField(User, to_field="id")
    book = ForeignKeyField(Book, to_field="id")
    date_of_begin_of_reading = DateField(null=False)
    date_of_end_of_reading = DateField(null=True)
    read = BooleanField(null=False, default=False)


class Favourites(BaseModel):
    id = AutoField()
    reader = ForeignKeyField(User, to_field="id")
    book = ForeignKeyField(Book, to_field="id")


db.create_tables([Role, User, Genre, Book, Formular, Favourites], safe=True)

if not Role.select().count():
    add_new_row(Role,
                {"code": "ADMIN",
                 "name": "Администратор"})

    add_new_row(Role,
                {"code": "LIBRARIAN",
                 "name": "Библиотекарь"})

    add_new_row(Role,
                {"code": "READER",
                 "name": "Читатель"})

if not User.select().count():
    file = open("data/admin.txt")

    add_new_row(User,
                {"login": file.readline()[:-1],
                 "email": file.readline()[:-1],
                 "password_hash": file.readline(),
                 "role": 1})
