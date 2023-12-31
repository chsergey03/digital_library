from modules.app import app
from modules.models import *

from flask import (request, render_template, redirect,
                   url_for, session, make_response)

from bcrypt import hashpw, checkpw, gensalt


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
    guest = not session.get("signed_in")
    not_reader = False
    admin = False
    login = ""

    if not guest:
        login = get_login_from_cookies()

        role_code = get_role_code()

        not_reader = role_code != "READER"
        admin = role_code == "ADMIN"

    return render_template("index.html",
                           login=login,
                           not_reader=not_reader,
                           admin=admin,
                           authenticated=session.get("signed_in"))


@app.route("/sign_in", methods=["POST", "GET"])
def sign_in():
    error = False

    if request.method == "POST":
        login_value = request.form.get("login")
        password_value = request.form.get("password")

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
        login_value = request.form.get("login")
        existing_login = is_there_value_of_field(User, "login", login_value)

        email_value = request.form.get("email")
        existing_email = is_there_value_of_field(User, "email", email_value)

        password_value = request.form.get("password")
        repeat_of_password_value = request.form.get("repeat_of_password")

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
    book_to_edit_id_request_arg = request.args.get("book_to_edit_id_request_arg")

    if book_to_edit_id_request_arg:
        books_query = (Book
                       .select()
                       .where(Book.id == book_to_edit_id_request_arg))

        book_to_edit = True
    else:
        books_query = Book.select()

        book_to_edit = False

    book_is_already_favourite = False
    book_without_genre = False
    book_cannot_be_deleted = False
    reader = False
    guest = not session.get("signed_in")

    if not guest:
        role_code = get_role_code()

        reader = role_code == "READER"

    genres_query = Genre.select() if not reader else None

    if request.method == "POST":
        book_id = request.form.get("book_button")
        book_to_edit_id = request.form.get("edit_book_button")

        title = request.form.get("title")
        author = request.form.get("author")
        publisher = request.form.get("publisher")
        release_year = request.form.get("release_year")
        genre_id = request.form.get("genres")

        if request.form.get("search_book_button"):
            title_substr = request.form.get("title_substr")
            books_query = Book.select().where(Book.title.contains(title_substr))
        elif request.form.get("export_to_json_button"):
            export_data_of_query_to_json(books_query, "books.json")
        elif request.form.get("export_to_csv_button"):
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
                id_in_favourites = is_there_value_of_field(Favourites, "book", book_id)
                id_in_formulars = is_there_value_of_field(Formular, "book", book_id)

                if (not id_in_formulars) and (not id_in_favourites):
                    delete_row_by_id(book_id, Book)
                else:
                    book_cannot_be_deleted = True
        elif book_to_edit_id:
            return redirect(url_for(
                "books",
                book_to_edit_id_request_arg=book_to_edit_id))
        elif request.form.get("enter"):
            if genre_id:
                row_data_dict = \
                    {"title": title,
                     "author": author,
                     "publisher": publisher,
                     "release_year": release_year,
                     "genre": genre_id}

                if book_to_edit_id_request_arg:
                    update_row(Book,
                               book_to_edit_id_request_arg,
                               row_data_dict)

                    return redirect(url_for(
                        "books",
                        book_to_edit_id_request_arg=None))
                else:
                    add_new_row(Book,
                                row_data_dict)
            else:
                book_without_genre = True

    return render_template(
        "books.html",
        guest=guest,
        reader=reader,
        book_is_already_favourite=book_is_already_favourite,
        book_without_genre=book_without_genre,
        book_cannot_be_deleted=book_cannot_be_deleted,
        book_to_edit=book_to_edit,
        genres=genres_query,
        books=books_query)


@app.route("/users", methods=["POST", "GET"])
def users():
    users_query = None
    roles_query = None

    guest = not session.get("signed_in") or get_role_code() != "ADMIN"
    user_role_to_edit = False

    if not guest:
        user_role_to_edit_id_request_arg = (
            request.args.get("user_role_to_edit_id_request_arg"))

        if user_role_to_edit_id_request_arg:
            users_query = (User
                           .select()
                           .where(User.id == user_role_to_edit_id_request_arg))

            user_which_role_is_edited = User.get(User.id == user_role_to_edit_id_request_arg)

            roles_query = Role.select().where(Role.id != user_which_role_is_edited.role)

            user_role_to_edit = True
        else:
            user = get_user_by_login()

            users_query = User.select().where(User.id != user.id)

            user_role_to_edit = False

        if request.method == "POST":
            user_role_to_edit_id = request.form.get("edit_user_role_button")

            if user_role_to_edit_id:
                return redirect(url_for(
                    "users",
                    user_role_to_edit_id_request_arg=user_role_to_edit_id))
            elif user_role_to_edit_id_request_arg:
                role_id = request.form.get("roles")

                update_row(User,
                           user_role_to_edit_id_request_arg,
                           {"role": role_id})

                return redirect(url_for(
                    "users",
                    user_role_to_edit_id_request_arg=None))

    return render_template("users.html",
                           guest=guest,
                           user_role_to_edit=user_role_to_edit,
                           roles=roles_query,
                           users=users_query)


@app.route("/formulars", methods=["POST", "GET"])
def formulars():
    formulars_query = None
    users_query = None
    books_query = None

    guest = not session.get("signed_in")
    reader = False
    formular_to_edit = False

    if not guest:
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
            formular_to_edit_id_request_arg = (
                request.args.get("formular_to_edit_id_request_arg"))

            if formular_to_edit_id_request_arg:
                formulars_query = (Formular
                                   .select()
                                   .where(Formular.id == formular_to_edit_id_request_arg))

                formular_to_edit = True
            else:
                formulars_query = Formular.select()

                formular_to_edit = False

            users_query = (User.select()
                           .where(User.role == Role.get(Role.code == "READER").id))

            books_query = Book.select()

            if request.method == "POST":
                formular_to_delete_id = request.form.get("delete_formular_button")
                formular_to_edit_id = request.form.get("edit_formular_button")

                user_id = request.form.get("users")
                book_id = request.form.get("books")

                add_user_without_user_or_book_id = (not user_id) or (not book_id)

                date_of_begin_of_reading = request.form.get("date_of_begin_of_reading")
                date_of_end_of_reading = request.form.get("date_of_begin_of_reading")
                was_book_read = True if request.form.get("was_book_read") else False

                if request.form.get("export_to_json_button"):
                    export_data_of_query_to_json(formulars_query, "formulars.json")
                elif request.form.get("export_to_csv_button"):
                    export_data_of_query_to_csv(formulars_query, "formulars.csv")
                elif formular_to_delete_id:
                    delete_row_by_id(formular_to_delete_id, Formular)
                elif formular_to_edit_id:
                    return redirect(url_for(
                        "formulars",
                        formular_to_edit_id_request_arg=formular_to_edit_id))
                elif request.form.get("enter") and not add_user_without_user_or_book_id:
                    row_data_dict = \
                        {"reader": user_id,
                         "book": book_id,
                         "date_of_begin_of_reading": date_of_begin_of_reading,
                         "date_of_end_of_reading": date_of_end_of_reading,
                         "read": was_book_read}

                    if formular_to_edit_id_request_arg:
                        update_row(Formular, formular_to_edit_id_request_arg, row_data_dict)

                        return redirect(url_for(
                            "formulars",
                            formular_to_edit_id_request_arg=None))
                    else:
                        add_new_row(Formular, row_data_dict)

    return render_template("formulars.html",
                           guest=guest,
                           reader=reader,
                           formular_to_edit=formular_to_edit,
                           users=users_query,
                           books=books_query,
                           formulars=formulars_query)


@app.route("/favourites", methods=["POST", "GET"])
def favourites():
    favourites_query = None

    guest = not session.get("signed_in")

    if not guest and get_role_code() == "READER":
        try_to_delete_row_through_form("delete_from_favourites",
                                       Favourites)

        favourites_query = (Favourites
                            .select()
                            .where(Favourites.reader == get_user_by_login().id))

    return render_template("favourites.html",
                           guest=guest,
                           favourites=favourites_query)


@app.route("/genres", methods=["POST", "GET"])
def genres():
    genres_query = None

    guest = not session.get("signed_in")
    existing_code_or_name = False
    genre_cannot_be_deleted = False
    genre_to_edit = False

    if not guest and get_role_code() != "READER":
        genre_to_edit_id_request_arg = request.args.get("genre_to_edit_id_request_arg")

        if genre_to_edit_id_request_arg:
            genres_query = (Genre
                            .select()
                            .where(Genre.id == genre_to_edit_id_request_arg))

            genre_to_edit = True
        else:
            genres_query = Genre.select()

            genre_to_edit = False

        if request.method == "POST":
            genre_to_delete_id = request.form.get("delete_genre_button")
            genre_to_edit_id = request.form.get("edit_genre_button")

            code = request.form.get("code")
            name = request.form.get("name")

            existing_code = is_there_value_of_field(Genre, "code", code)
            existing_name = is_there_value_of_field(Genre, "name", name)

            existing_code_or_name = existing_code or existing_name

            if genre_to_delete_id:
                id_in_books = is_there_value_of_field(Book, "genre", genre_to_delete_id)

                if not id_in_books:
                    delete_row_by_id(genre_to_delete_id, Genre)
                else:
                    genre_cannot_be_deleted = True
            elif genre_to_edit_id:
                return redirect(url_for(
                    "genres",
                    genre_to_edit_id_request_arg=genre_to_edit_id))
            elif genre_to_edit_id_request_arg:
                existing_code_not_in_this_row = (
                    is_there_value_of_field_not_in_this_row(
                        Genre, "code", code, genre_to_edit_id_request_arg))

                existing_name_not_in_this_row = (
                    is_there_value_of_field_not_in_this_row(
                        Genre, "name", name, genre_to_edit_id_request_arg))

                existing_code_or_name_not_in_this_row = (
                        existing_code_not_in_this_row or existing_name_not_in_this_row)

                if not existing_code_or_name_not_in_this_row:
                    update_row(Genre,
                               genre_to_edit_id_request_arg,
                               {"code": code,
                                "name": name})

                    return redirect(url_for(
                        "genres",
                        genre_to_edit_id_request_arg=None))
            elif not existing_code_or_name and request.form.get("enter"):
                add_new_row(Genre,
                            {"code": code,
                             "name": name})

    return render_template("genres.html",
                           guest=guest,
                           existing_code_or_name=existing_code_or_name,
                           genre_cannot_be_deleted=genre_cannot_be_deleted,
                           genre_to_edit=genre_to_edit,
                           genres=genres_query)
