from modules.app import db

from peewee import *


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    login = CharField(max_length=250, null=False, unique=True)
    email = CharField(max_length=250, null=True, unique=True)
    password_hash = CharField(max_length=250, null=False, unique=False)

    @staticmethod
    def add_new(login, email, password_hash):
        new_user = User(login=login,
                        email=email,
                        password_hash=password_hash)

        new_user.save()

    @staticmethod
    def is_there_value_of_field(field, value):
        return len(User.select().where(getattr(User, field) == value)) != 0


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
