from flask import Flask
from peewee import PostgresqlDatabase

app = Flask(__name__, template_folder="../templates")
app.config.from_object(__name__)

db = PostgresqlDatabase(database="digital_library",
                        user="postgres",
                        password="password",
                        host="localhost",
                        port=5432)

db.connect()
