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
    login_error_message = ""
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

        if username != Users.username or password != Users.password:
            login_error_message = "username or password invalid"

        # query database user table / get username
        user = Users.query.filter_by(
            username=request.form.get('username')).first()

        if user:
            # session for logged in user
            session['user_id'] = user.id
            return redirect('/notes')
        else:

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
        new_note = Notes(
            user_id=user,
            note_title=title,
            note_subject=subject,
            created_on=current_date
        )

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
@check_login
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
            page_id=note_id,
            page_title=page_title,
            created_on=current_date,
        )

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


@app.route("/note/<string:title>/page/<string:page>/", methods=["GET"])
def note(title, page):

    user = session['user_id']

    note_id = db.session.query(Page).filter(Page.page_title == page)

    get_page_id = db.session.query(Page.id).filter(Page.page_title == page)

    get_bookmark_id = db.session.query(
        BookMarks).filter(BookMarks.page_id == get_page_id)

    bookmark_total = db.session.query(BookMarks).count()
    sidenote_total = db.session.query(SideNotes).count()

    blocks = db.session.query(Blocks).filter(
        Blocks.page_id == get_page_id)

    return render_template("page.html", title=title, page=page, blocks=blocks, bookmark_total=bookmark_total, sidenote_total=sidenote_total, bookmarks=get_bookmark_id)


@app.route("/note/<string:title>/page/<string:page>/new_block", methods=["GET", "POST"])
def block_form(title, page):

    if request.method == "POST":
        user = session['user_id']

        block_title = request.form.get('block-title')
        block_body = request.form.get('block-body')

        sanitize_block_title = bleach.clean(block_title)
        sanitize_block_body = bleach.clean(block_body)

        get_page = db.session.query(Page).filter(
            Page.page_title == page).first()

        new_block = Blocks(
            created_on=current_date,
            block_title=sanitize_block_title,
            page_id=get_page.id,
            block_notes=sanitize_block_body,
        )

        try:
            db.session.add(new_block)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        return redirect(f"/note/{title}/page/{page}")
    else:
        blocking = "hello"
        return render_template("block.html", blocks=blocking, title=title, page=page)


@app.route("/note/<string:title>/page/<string:page>/bookmark", methods=["GET", "POST"])
def page_bookmark(title, page):

    if request.method == "POST":

        # sesssion id of he logged in user
        user = session['user_id']

        # get the name field from the form (url / title)
        bookmark_url = request.form.get('bookmark_url')
        bookmark_title = request.form.get('bookmark_title')

        page_id = db.session.query(Page, BookMarks).filter(
            BookMarks.page_id == Page.id)

        print(page_id)

        new_bookmark = BookMarks(
            bookmark_url=bookmark_url,
            created_on=current_date,
            page_id=page_id,
            bookmark_title=bookmark_title
        )
        print(new_bookmark)
        try:
            db.session.add(new_bookmark)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
        finally:
            db.session.close()

        return redirect(f"/note/{title}/page/{page}")
    else:
        return render_template("bookmark.html", title=title, page=page)


@app.route("/note/<string:title>/page/<string:page>/sidenote", methods=["GET", "POST"])
def page_sidenote(title, page):

    if request.method == "POST":
        user = session['user_id']
        sidenote = request.form.get("sidenote")
        page_id = db.session.query(Page.id).filter(Page.page_title == page)

        new_sidenote = SideNotes(
            sidenotes=sidenote,
            created_on=current_date,
            page_id=page_id
        )

        db.session.add(new_sidenote)
        db.session.commit()

        db.session.close()

        return redirect(f"/note/{title}/page/{page}")
    else:
        return render_template("sidenote.html", title=title, page=page)


@app.route("/note/<string:title>/page/<string:page>/block/<int:id>/edit", methods=["GET", "POST"])
def page_edit(title, page, id):

    user = session['user_id']
    block = db.session.query(Blocks).filter(Blocks.id == id)
    return render_template("editBlock.html", title=title, page=page, block=block)


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Successfully logged out")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
