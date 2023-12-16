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


db.create_tables([User], safe=True)
