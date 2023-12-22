from flask import Flask, session
from peewee import PostgresqlDatabase

app = Flask(__name__, template_folder="../templates")
app.config.from_object(__name__)
app.config["SECRET_KEY"] = "24dd3efb29964ff789bd1132af3d1bfe"

db = PostgresqlDatabase(database="digital_library",
                        user="postgres",
                        password="password",
                        host="localhost",
                        port=5432)

db.connect()
