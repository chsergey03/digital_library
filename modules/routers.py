from modules.app import app
from modules.models import *

from flask import request, render_template, redirect, url_for, session
from bcrypt import hashpw, checkpw, gensalt
from enum import StrEnum


class FormsNames(StrEnum):
    LOGIN = "login"
    EMAIL = "email"
    PASSWORD = "password"
    REPEAT_OF_PASSWORD = "repeat_of_password"


def init_session(login_value):
    session["signed_in"] = True
    session["login"] = login_value


def drop_session():
    session["signed_in"] = False
    session["login"] = ""


@app.route("/")
def index():
    return render_template("index.html",
                           authenticated=session.get("signed_in"))


@app.route("/sign_in", methods=["POST", "GET"])
def sign_in():
    error = False

    if request.method == "POST":
        login_value = request.form.get(FormsNames.LOGIN)
        password_value = request.form.get(FormsNames.PASSWORD)

        query = (User
                 .select(User.password_hash)
                 .where(User.login == login_value))

        query_dicts = query.dicts()

        if (len(query_dicts) > 0 and
                checkpw(password_value.encode("utf-8"),
                        query_dicts[0]["password_hash"])):
            init_session(login_value)

            return redirect(url_for("index", authenticated=True))
        else:
            error = True

    return render_template("sign_in.html", error=error)


@app.route("/sign_out")
def sign_out():
    drop_session()

    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    existing_login, existing_email, mismatched_passwords = False, False, False

    if request.method == "POST":
        login_value = request.form.get(FormsNames.LOGIN)
        existing_login = is_there_value_of_field(User, FormsNames.LOGIN, login_value)

        email_value = request.form.get(FormsNames.EMAIL)
        existing_email = is_there_value_of_field(User, FormsNames.EMAIL, email_value)

        password_value = request.form.get(FormsNames.PASSWORD)
        repeat_of_password_value = request.form.get(FormsNames.REPEAT_OF_PASSWORD)

        mismatched_passwords = password_value != repeat_of_password_value

        if (not existing_login) and (not existing_login) and (not mismatched_passwords):
            salt = gensalt()
            password_hash = hashpw(password_value.encode("utf8"), salt)

            add_new_row(User,
                        {"login": login_value,
                         "email": email_value,
                         "password_hash": password_hash})

            init_session(login_value)

            return redirect(url_for("index"))

    return render_template("register.html",
                           existing_login=existing_login,
                           existing_email=existing_email,
                           mismatched_passwords=mismatched_passwords)


@app.route("/books", methods=["POST", "GET"])
def books():
    books_query = Book.select()

    if request.method == "POST":
        if request.form.get("search_book_button") == "Найти издание":
            title_substr = request.form.get("title_substr")

            books_query = Book.select().where(Book.title.contains(title_substr))
        elif (request.form.get("export_to_json_button")
              == "Экспорт всей таблицы в формат JSON"):
            export_data_of_query_to_json(books_query, "books.json")
        elif (request.form.get("export_to_csv_button")
              == "Экспорт всей таблицы в формат CSV"):
            export_data_of_query_to_csv(books_query, "books.csv")

    return render_template("books.html", books=books_query)


@app.route("/users")
def users():
    users_query = None

    if session.get("signed_in"):
        users_query = User.select()

    return render_template("users.html", users=users_query)


@app.route("/formulars")
def formulars():
    formulars_query = None

    if session.get("signed_in"):
        formulars_query = Formular.select()

    return render_template("formulars.html", formulars=formulars_query)
