import os
from flask import Flask, render_template, request, flash, session, jsonify, url_for, redirect
from sqlalchemy import text, select
from flask_session import Session
from helper import error_message
from werkzeug.security import generate_password_hash, check_password_hash
from formModels import NoteBlock
from dotenv import load_dotenv
import bleach
from models import db, Users, Notes, SideNotes, Blocks, BookMarks
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
            return redirect('/dashboard')
        else:
            if username != Users.username or password != Users.password:
                login_error_message = "username or password invalid"
                return render_template("login.html", username=username_msg, password=password_msg, error=login_error_message)

    return render_template('login.html')


@app.route("/dashboard", methods=["GET", "POST"], endpoint='dashboard')
@check_login
def dashboard():

    if request.method == "GET":
        if 'user_id' in session:
            # user session
            user = session['user_id']

            # query to get logged in username
            get_logged_in_username = db.session.query(Users.username).filter(
                Users.id == user).first()[0]

            get_user_notes = db.session.query(
                Notes).filter(Notes.user_id == user)

            total_note_count = db.session.query(
                Notes).filter(Notes.user_id == user).count()

            db.session.close()

            return render_template("dashboard.html", username=get_logged_in_username, notes=get_user_notes, count=total_note_count, msg="Create your first Note")
    return render_template('dashboard.html')


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

        db.session.add(new_note)
        db.session.commit()
        db.session.close()

        return redirect('/dashboard')

    else:
        return render_template("notes.html")


@app.route("/note/<string:title>", methods=['GET', 'POST'])
def note_page(title):
    return title


@app.route("/note/<string:title>/<string:note>/")
def note(title, note):
    return render_template("note.html", title="hello", note="new note")


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Successfully logged out")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
