from modules.app import app
from modules.models import *

from flask import (request, render_template, redirect,
                   url_for, session, make_response)

from bcrypt import hashpw, checkpw, gensalt
from enum import StrEnum


class FormsNames(StrEnum):
    LOGIN = "login"
    EMAIL = "email"
    PASSWORD = "password"
    REPEAT_OF_PASSWORD = "repeat_of_password"


def init_session():
    session["signed_in"] = True


def get_response_of_initialized_session(login_value):
    response = make_response(redirect(url_for("index")))
    response.set_cookie("login", login_value, 60 * 60 * 24 * 15)

    return response


def drop_session():
    session["signed_in"] = False


def get_response_of_dropped_session():
    response = make_response(render_template("index.html"))
    response.delete_cookie("login")

    return response


@app.route("/")
def index():
    not_reader = False

    if session.get("signed_in") and not session.new:
        role_code = get_role_code()

        not_reader = role_code != "READER"

    return render_template("index.html",
                           not_reader=not_reader,
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
            init_session()

            return get_response_of_initialized_session(login_value)
        else:
            error = True

    return render_template("sign_in.html", error=error)


@app.route("/sign_out")
def sign_out():
    drop_session()

    return get_response_of_dropped_session()


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

        if (not existing_login) and (not existing_email) and (not mismatched_passwords):
            salt = gensalt()
            password_hash = hashpw(password_value.encode("utf8"), salt)

            add_new_row(User,
                        {"login": login_value,
                         "email": email_value,
                         "password_hash": password_hash,
                         "role": 3})

            init_session()

            return get_response_of_initialized_session(login_value)

    return render_template("register.html",
                           existing_login=existing_login,
                           existing_email=existing_email,
                           mismatched_passwords=mismatched_passwords)


@app.route("/books", methods=["POST", "GET"])
def books():
    books_query = Book.select()

    book_is_already_favourite = False

    reader = get_role_code() == "READER"

    if request.method == "POST":
        book_id = request.form.get("book_button")

        if request.form.get("search_book_button") == "Найти издание":
            title_substr = request.form.get("title_substr")

            books_query = (Book
                           .select()
                           .where(Book.title.contains(title_substr)))

        elif (request.form.get("export_to_json_button")
              == "Экспорт всей таблицы в формат JSON"):
            export_data_of_query_to_json(books_query, "books.json")
        elif (request.form.get("export_to_csv_button")
              == "Экспорт всей таблицы в формат CSV"):
            export_data_of_query_to_csv(books_query, "books.csv")
        elif book_id:
            if reader:
                user_id = get_user_by_login().id

                query = (Favourites
                         .select()
                         .where(Favourites.reader == user_id,
                                Favourites.book == book_id))

                if len(query.dicts()) == 0:
                    add_new_row(Favourites,
                                {"reader": user_id,
                                 "book": book_id})
                else:
                    book_is_already_favourite = True
            else:
                delete_row_by_id(book_id, Book)

    return render_template("books.html",
                           reader=reader,
                           book_is_already_favourite=book_is_already_favourite,
                           books=books_query)


@app.route("/users")
def users():
    users_query = None

    role_code = get_role_code()

    if session.get("signed_in") and role_code != "READER":
        users_query = User.select()

    return render_template("users.html",
                           users=users_query)


@app.route("/formulars", methods=["POST", "GET"])
def formulars():
    formulars_query = None
    reader = False

    login = get_login_from_cookies()

    if session.get("signed_in") and login:
        user = get_user_by_login()

        role_code = (Role
                     .get(Role.id == user.role)
                     .code)

        if role_code == "READER":
            reader = True

            formulars_query = (Formular
                               .select()
                               .where(Formular.reader == user.id))
        else:
            try_to_delete_row_through_form("delete_formular",
                                           Formular)

            formulars_query = Formular.select()

    return render_template("formulars.html",
                           reader=reader,
                           formulars=formulars_query)


@app.route("/favourites", methods=["POST", "GET"])
def favourites():
    favourites_query = None

    if get_role_code() == "READER":
        try_to_delete_row_through_form("delete_from_favourites",
                                       Favourites)

        favourites_query = (Favourites
                            .select()
                            .where(Favourites.reader == get_user_by_login().id))

    return render_template("favourites.html",
                           favourites=favourites_query)
