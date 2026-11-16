
import os
import re
import uuid
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.security import generate_password_hash, check_password_hash


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

# app.py is inside the website folder.
# BASE_DIR points to the main project folder.
BASE_DIR = Path(__file__).resolve().parent.parent
WEBSITE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(WEBSITE_DIR / "templates"),
    static_folder=str(WEBSITE_DIR / "static")
)

# The .env file is in the main project folder.
load_dotenv(BASE_DIR / ".env")

app.secret_key = os.getenv("SECRET_KEY", "library-dev-key")

UPLOAD_FOLDER = WEBSITE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


# --------------------------------------------------
# IMAGE FUNCTIONS
# --------------------------------------------------

def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_uploaded_image(image):
    if not image or not image.filename:
        return None

    if not allowed_image(image.filename):
        raise ValueError(
            "Invalid image format. Use PNG, JPG, JPEG, or WEBP."
        )

    extension = Path(image.filename).suffix.lower()
    filename = f"{uuid.uuid4().hex}{extension}"

    image.save(UPLOAD_FOLDER / filename)
    return f"uploads/{filename}"


def delete_uploaded_image(image_path):
    if not image_path:
        return

    path = (UPLOAD_FOLDER / Path(image_path).name).resolve()

    if path.parent == UPLOAD_FOLDER.resolve() and path.is_file():
        path.unlink()


# --------------------------------------------------
# DATABASE CONNECTIONS
# --------------------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "library_auth_db")
    )


def get_library_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database="library_db"
    )


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.fullmatch(pattern, email) is not None


def is_logged_in():
    return "user_id" in session


def require_login():
    if not is_logged_in():
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    return None


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("library"))

    return redirect(url_for("login"))


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        identifier = (
            request.form.get("email", "").strip()
            or request.form.get("username", "").strip()
            or request.form.get("identifier", "").strip()
        )

        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Please enter your username/email and password.", "error")
            return redirect(url_for("login"))

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT user_id, username, email, password_hash
                FROM USERS
                WHERE username = %s OR email = %s
                """,
                (identifier, identifier)
            )

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password_hash"], password
            ):
                session.clear()
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]

                flash("Login successful!", "success")
                return redirect(url_for("library"))

            flash("Invalid username/email or password.", "error")

        except mysql.connector.Error:
            app.logger.exception("Login database error")
            flash("Could not connect to the database. Check your settings.", "error")

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    return render_template("login.html")


# --------------------------------------------------
# REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        confirm_password = request.form.get(
            "confirm_password",
            request.form.get("confirm-password", "")
        )

        if not username or not email or not password:
            flash("Please complete all required fields.", "error")
            return redirect(url_for("register"))

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        if confirm_password and password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO USERS (username, email, password_hash)
                VALUES (%s, %s, %s)
                """,
                (username, email, password_hash)
            )

            connection.commit()

            flash("Registration successful. You can now log in.", "success")
            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:
            if connection:
                connection.rollback()

            flash("That username or email may already be registered.", "error")

        except mysql.connector.Error:
            if connection:
                connection.rollback()

            app.logger.exception("Registration database error")
            flash("Registration failed. Check your database settings.", "error")

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    return render_template("register.html")


# --------------------------------------------------
# LOG OUT
# --------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# --------------------------------------------------
# LIBRARY DASHBOARD
# F2.1 SEARCH BOOKS
# F2.2 CATALOGUE
# F2.3 REPORTS
# --------------------------------------------------

@app.route("/library")
def library():

    guard = require_login()
    if guard:
        return guard

    keyword = request.args.get("keyword", "").strip()
    min_price_text = request.args.get("min_price", "").strip()
    max_price_text = request.args.get("max_price", "").strip()
    selected_categories = request.args.getlist("category_id")

    try:
        min_price = float(min_price_text) if min_price_text else None
        max_price = float(max_price_text) if max_price_text else None

        if min_price is not None and min_price < 0:
            raise ValueError

        if max_price is not None and max_price < 0:
            raise ValueError

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise ValueError

        selected_categories = [int(x) for x in selected_categories]

        if any(x <= 0 for x in selected_categories):
            raise ValueError

    except ValueError:
        flash("Please enter a valid price range and category selection.", "error")
        return redirect(url_for("library"))

    connection = None
    cursor = None

    try:
        connection = get_library_connection()
        cursor = connection.cursor(dictionary=True)

        # Get authors.
        cursor.execute(
            """
            SELECT author_id, name, country, author_image
            FROM AUTHOR
            ORDER BY author_id
            """
        )
        authors = cursor.fetchall()

        # Get categories.
        cursor.execute(
            """
            SELECT category_id, name
            FROM CATEGORY
            ORDER BY name
            """
        )
        categories = cursor.fetchall()

        # F2.1: SEARCH BOOKS.
        search_sql = """
            SELECT
                b.book_id,
                b.title,
                b.price,
                b.author_id,
                b.cover_image
            FROM BOOK b
            WHERE (%s = '' OR b.title LIKE %s)
              AND (%s IS NULL OR b.price >= %s)
              AND (%s IS NULL OR b.price <= %s)
        """

        search_params = [
            keyword,
            f"%{keyword}%",
            min_price,
            min_price,
            max_price,
            max_price
        ]

        if selected_categories:
            placeholders = ", ".join(
                ["%s"] * len(selected_categories)
            )

            search_sql += f" AND b.category_id IN ({placeholders})"
            search_params.extend(selected_categories)

        search_sql += " ORDER BY b.price ASC"

        cursor.execute(search_sql, tuple(search_params))
        books = cursor.fetchall()

        # F2.2: CATALOGUE.
        cursor.execute(
            """
            SELECT
                b.book_id,
                b.title,
                b.price,
                b.publish_year,
                b.cover_image,
                a.name AS author_name,
                p.name AS publisher_name,
                c.name AS category_name
            FROM BOOK b
            JOIN AUTHOR a
                ON b.author_id = a.author_id
            LEFT JOIN PUBLISHER p
                ON b.publisher_id = p.publisher_id
            LEFT JOIN CATEGORY c
                ON b.category_id = c.category_id
            ORDER BY b.title
            """
        )

        catalogue_books = cursor.fetchall()

        # F2.3 REPORT 1: CATEGORY REPORT.
        cursor.execute(
            """
            SELECT
                c.category_id,
                c.name AS category_name,
                COUNT(b.book_id) AS book_count,
                ROUND(AVG(b.price), 2) AS average_price
            FROM CATEGORY c
            LEFT JOIN BOOK b
                ON c.category_id = b.category_id
            GROUP BY c.category_id, c.name
            ORDER BY c.name
            """
        )

        category_reports = cursor.fetchall()

        # F2.3 REPORT 2: AUTHORS WITH AT LEAST TWO BOOKS.
        cursor.execute(
            """
            SELECT
                a.author_id,
                a.name AS author_name,
                COUNT(b.book_id) AS book_count
            FROM AUTHOR a
            JOIN BOOK b
                ON a.author_id = b.author_id
            GROUP BY a.author_id, a.name
            HAVING COUNT(b.book_id) >= 2
            ORDER BY book_count DESC, a.name
            """
        )

        prolific_authors = cursor.fetchall()

        # F2.3 REPORT 3: OVERALL PRICE STATISTICS.
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_books,
                COALESCE(ROUND(SUM(price), 2), 0) AS total_price,
                COALESCE(ROUND(MIN(price), 2), 0) AS minimum_price,
                COALESCE(ROUND(MAX(price), 2), 0) AS maximum_price
            FROM BOOK
            """
        )

        price_report = cursor.fetchone()

        return render_template(
            "library.html",
            books=books,
            authors=authors,
            categories=categories,
            catalogue_books=catalogue_books,
            category_reports=category_reports,
            prolific_authors=prolific_authors,
            price_report=price_report,
            keyword=keyword,
            min_price=min_price_text,
            max_price=max_price_text,
            selected_categories=[
                str(x) for x in selected_categories
            ]
        )

    except mysql.connector.Error:
        app.logger.exception("Library database error")
        flash("Could not load the library. Check the database connection.", "error")
        return redirect(url_for("login"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# --------------------------------------------------
# ADD A BOOK
# --------------------------------------------------

@app.route("/books/add", methods=["POST"])
def add_book():

    guard = require_login()
    if guard:
        return guard

    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    author_id_text = request.form.get("author_id", "").strip()
    image = request.files.get("cover_image")

    if not title or not price_text or not author_id_text:
        flash("Please complete all required book fields.", "error")
        return redirect(url_for("library"))

    try:
        price = float(price_text)
        author_id = int(author_id_text)

        if price < 0:
            raise ValueError

    except ValueError:
        flash("Enter a valid price and select an author.", "error")
        return redirect(url_for("library"))

    connection = None
    cursor = None
    image_path = None

    try:
        if image and image.filename:
            image_path = save_uploaded_image(image)

        connection = get_library_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO BOOK (title, price, author_id, cover_image)
            VALUES (%s, %s, %s, %s)
            """,
            (title, price, author_id, image_path)
        )

        connection.commit()
        flash("Book added successfully!", "success")

    except ValueError as error:
        flash(str(error), "error")

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        if image_path:
            delete_uploaded_image(image_path)

        app.logger.exception("Add book database error")
        flash("Could not add the book. Check the selected author and database.", "error")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for("library"))


# --------------------------------------------------
# ADD AN AUTHOR
# --------------------------------------------------

@app.route("/authors/add", methods=["POST"])
def add_author():

    guard = require_login()
    if guard:
        return guard

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("author_image")

    if not name:
        flash("Author name is required.", "error")
        return redirect(url_for("library"))

    connection = None
    cursor = None
    image_path = None

    try:
        if image and image.filename:
            image_path = save_uploaded_image(image)

        connection = get_library_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO AUTHOR (name, country, author_image)
            VALUES (%s, %s, %s)
            """,
            (name, country or None, image_path)
        )

        connection.commit()
        flash("Author added successfully!", "success")

    except ValueError as error:
        flash(str(error), "error")

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        if image_path:
            delete_uploaded_image(image_path)

        app.logger.exception("Add author database error")
        flash("Could not add the author.", "error")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for("library"))


# --------------------------------------------------
# EDIT A BOOK
# --------------------------------------------------

@app.route("/books/edit/<int:book_id>", methods=["POST"])
def edit_book(book_id):

    guard = require_login()
    if guard:
        return guard

    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    author_id_text = request.form.get("author_id", "").strip()
    image = request.files.get("cover_image")

    if not title or not price_text or not author_id_text:
        flash("Please complete all required book fields.", "error")
        return redirect(url_for("library"))

    try:
        price = float(price_text)
        author_id = int(author_id_text)

        if price < 0:
            raise ValueError

    except ValueError:
        flash("Enter a valid price and select an author.", "error")
        return redirect(url_for("library"))

    connection = None
    cursor = None
    new_image_path = None
    old_image_path = None

    try:
        connection = get_library_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT cover_image FROM BOOK WHERE book_id = %s",
            (book_id,)
        )

        book = cursor.fetchone()

        if not book:
            flash("Book not found.", "error")
            return redirect(url_for("library"))

        old_image_path = book["cover_image"]

        if image and image.filename:
            new_image_path = save_uploaded_image(image)

            cursor.execute(
                """
                UPDATE BOOK
                SET title = %s,
                    price = %s,
                    author_id = %s,
                    cover_image = %s
                WHERE book_id = %s
                """,
                (title, price, author_id, new_image_path, book_id)
            )

        else:
            cursor.execute(
                """
                UPDATE BOOK
                SET title = %s,
                    price = %s,
                    author_id = %s
                WHERE book_id = %s
                """,
                (title, price, author_id, book_id)
            )

        connection.commit()

        if new_image_path and old_image_path:
            delete_uploaded_image(old_image_path)

        flash("Book updated successfully!", "success")

    except ValueError as error:
        flash(str(error), "error")

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        if new_image_path:
            delete_uploaded_image(new_image_path)

        app.logger.exception("Edit book database error")
        flash("Could not update the book.", "error")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for("library"))


# --------------------------------------------------
# EDIT AN AUTHOR
# --------------------------------------------------

@app.route("/authors/edit/<int:author_id>", methods=["POST"])
def edit_author(author_id):

    guard = require_login()
    if guard:
        return guard

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("author_image")

    if not name:
        flash("Author name is required.", "error")
        return redirect(url_for("library"))

    connection = None
    cursor = None
    new_image_path = None
    old_image_path = None

    try:
        connection = get_library_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT author_image FROM AUTHOR WHERE author_id = %s",
            (author_id,)
        )

        author = cursor.fetchone()

        if not author:
            flash("Author not found.", "error")
            return redirect(url_for("library"))

        old_image_path = author["author_image"]

        if image and image.filename:
            new_image_path = save_uploaded_image(image)

            cursor.execute(
                """
                UPDATE AUTHOR
                SET name = %s,
                    country = %s,
                    author_image = %s
                WHERE author_id = %s
                """,
                (name, country or None, new_image_path, author_id)
            )

        else:
            cursor.execute(
                """
                UPDATE AUTHOR
                SET name = %s,
                    country = %s
                WHERE author_id = %s
                """,
                (name, country or None, author_id)
            )

        connection.commit()

        if new_image_path and old_image_path:
            delete_uploaded_image(old_image_path)

        flash("Author updated successfully!", "success")

    except ValueError as error:
        flash(str(error), "error")

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        if new_image_path:
            delete_uploaded_image(new_image_path)

        app.logger.exception("Edit author database error")
        flash("Could not update the author.", "error")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for("library"))


# --------------------------------------------------
# DELETE A BOOK
# --------------------------------------------------

@app.route("/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):

    guard = require_login()
    if guard:
        return guard

    connection = None
    cursor = None
    image_path = None

    try:
        connection = get_library_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT cover_image FROM BOOK WHERE book_id = %s",
            (book_id,)
        )

        book = cursor.fetchone()

        if not book:
            flash("Book not found.", "error")
            return redirect(url_for("library"))

        image_path = book["cover_image"]

        cursor.execute(
            "DELETE FROM BOOK WHERE book_id = %s",
            (book_id,)
        )

        connection.commit()

        if image_path:
            delete_uploaded_image(image_path)

        flash("Book deleted successfully!", "success")

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        app.logger.exception("Delete book database error")
        flash("Could not delete the book.", "error")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for("library"))


# --------------------------------------------------
# DELETE AN AUTHOR
# --------------------------------------------------

@app.route("/authors/delete/<int:author_id>", methods=["POST"])
def delete_author(author_id):

    guard = require_login()
    if guard:
        return guard

    connection = None
    cursor = None
    author_image_path = None
    book_image_paths = []

    try:
        connection = get_library_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT author_image FROM AUTHOR WHERE author_id = %s",
            (author_id,)
        )

        author = cursor.fetchone()

        if not author:
            flash("Author not found.", "error")
            return redirect(url_for("library"))

        author_image_path = author["author_image"]

        cursor.execute(
            "SELECT cover_image FROM BOOK WHERE author_id = %s",
            (author_id,)
        )

        book_image_paths = [
            row["cover_image"]
            for row in cursor.fetchall()
            if row["cover_image"]
        ]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM BOOK WHERE author_id = %s",
            (author_id,)
        )

        book_count = cursor.fetchone()["total"]

        # The foreign key deletes the author's books automatically.
        cursor.execute(
            "DELETE FROM AUTHOR WHERE author_id = %s",
            (author_id,)
        )

        connection.commit()

        if author_image_path:
            delete_uploaded_image(author_image_path)

        for image_path in book_image_paths:
            delete_uploaded_image(image_path)

        flash(
            f"Author deleted successfully. {book_count} associated book(s) deleted.",
            "success"
        )

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        app.logger.exception("Delete author database error")
        flash("Could not delete the author.", "error")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for("library"))


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
