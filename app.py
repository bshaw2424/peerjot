import os
from flask import Flask, render_template, request, flash, session, jsonify, url_for, redirect
from sqlalchemy import text, select
from flask_session import Session
from helper import error_message
from werkzeug.security import generate_password_hash, check_password_hash
from formModels import NoteBlock
from dotenv import load_dotenv
import bleach
from models import db, Users, Notes, SideNotes, Blocks, BookMarks, Page
from flask_migrate import Migrate
import datetime
import secrets
current_date = datetime.datetime.now()
load_dotenv()  # take environment variables from .env.

app = Flask(__name__)


app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DB_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Session(app)

db.init_app(app)
migrate = Migrate

with app.app_context():
    db.create_all()


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        new_user = Users(username=username, password=password,
                         created_on=current_date)

        db.session.add(new_user)
        db.session.commit()
        db.session.close()

        flash("account created successfully")
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # variables if the username/password left blank
        username_msg = ""
        password_msg = ""

        if not username:
            username_msg = "Username is required"
        if not password:
            password_msg = "Password is required"

        # query database user table / get username
        user = Users.query.filter_by(
            username=request.form.get('username')).first()

        if user:
            # session for logged in user
            session['user_id'] = user.id
            return redirect('/notes')
        else:
            if username != Users.username or password != Users.password:
                login_error_message = "username or password invalid"
                return render_template("login.html", username=username_msg, password=password_msg, error=login_error_message)

    return render_template('login.html')


@app.route("/new_note", methods=["GET", "POST"], endpoint='new_note')
@check_login
def new_route():

    if request.method == "POST":
        user = session['user_id']
        # form data

        title = request.form.get("note-title")
        subject = request.form.get("note-subject")

        title_msg = ""
        subject_msg = ""

        # create new note and add to database
        new_note = Notes(note_title=title, user_id=user, note_subject=subject,
                         created_on=current_date)

        if not title:
            title_msg = "Note title is required"
        if not subject:
            subject_msg = "Note Subject is required"
        try:
            db.session.add(new_note)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        return redirect("/notes")

    else:
        return render_template("notes.html")


@app.route("/notes", methods=["GET", "POST"])
def notes():

    user = session['user_id']

    notes = db.session.query(
        Notes).filter(Notes.user_id == user)

    note_count = db.session.query(Notes).filter(
        Notes.user_id == user).count()

    return render_template("note_index.html", notes=notes, count=note_count, count_message="Currently No Notes")


@app.route("/note/<string:title>/create_page", methods=["GET", "POST"])
def create_page(title):

    if request.method == "POST":
        user = session['user_id']

        page_title = request.form.get("title")

        note_id = db.session.query(Notes.id).filter(
            Notes.note_title == title)

        # create new page for current note
        create_new_page = Page(
            page_id=note_id, page_title=page_title, created_on=current_date, user_id=user)
        print(create_new_page)
        print(note_id)

        try:
            db.session.add(create_new_page)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        return redirect(f"/note/{title}")
    else:
        return render_template('_pageForm.html', title=title)


@app.route("/note/<string:title>", methods=['GET', 'POST'])
def note_page(title):

    user = session['user_id']

    note_id = db.session.query(Notes.id).filter(
        Notes.note_title == title)

    pages = db.session.query(Page).filter(Page.page_id == note_id)
    page_count = pages.count()
    page_length = db.session.query(Page).filter(
        Page.page_id == user).count()
    return render_template("pages_index.html", title=title, page_length=page_length, pages=pages, count=page_count)


@app.route("/note/<string:title>/page/<string:page>/", methods=["GET", "POST"])
def note(title, page):

    user = session['user_id']
    note_id = db.session.query(Notes.id).filter(Notes.note_title == title)

    pages = db.session.query(Page).filter(Page.page_title == page)

    return render_template("page.html", title=title, page=pages)


@app.route("/note/<string:title>/page/<string:page>/bookmark", methods=["GET", "POST"])
def page_bookmark(title, page):

    user = session['user_id']

    return render_template("bookmark.html", title=title, page=page)


@app.route("/note/<string:title>/page/<string:page>/sidenote", methods=["GET", "POST"])
def page_sidenote(title, page):

    user = session['user_id']
    print(page)
    print(title)

    return render_template("sidenote.html", title=title, page=page)


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Successfully logged out")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
