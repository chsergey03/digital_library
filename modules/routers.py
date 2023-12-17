from modules.app import app
from modules.models import *

from flask import request, render_template, redirect, url_for
from bcrypt import hashpw, checkpw, gensalt
from enum import StrEnum


class FormsNames(StrEnum):
    LOGIN = "login"
    EMAIL = "email"
    PASSWORD = "password"
    REPEAT_OF_PASSWORD = "repeat_of_password"


@app.route("/")
def index():
    return render_template("index.html",
                           authorized=request.args.get("authorized"))


@app.route("/sign_in", methods=["GET", "POST"])
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
                checkpw(password_value.encode("utf-8"), query_dicts[0]["password_hash"])):
            return redirect(url_for("index", authorized=True))
        else:
            error = True

    return render_template("sign_in.html", error=error)


@app.route("/log_out")
def log_out():
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

            return redirect(url_for("index", authorized=True))

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
        elif request.form.get("export_to_json_button") == "Экспорт в JSON":
            export_data_of_query_to_json(books_query, "books.json")
        elif request.form.get("export_to_csv_button") == "Экспорт в CSV":
            export_data_of_query_to_csv(books_query, "books.csv")

    return render_template("books.html", books=books_query)
