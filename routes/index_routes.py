from flask import Blueprint, render_template, url_for, redirect, session, request
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks
import bleach
import datetime
current_date = datetime.datetime.now()

main = Blueprint('Index', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
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

        return redirect(url_for("login"))


@main.route("/login", methods=["GET", "POST"])
def login():

    session.clear()
    login_error_message = ""

    username = request.form.get("username")
    password = request.form.get("password")

    if request.method == "POST":
        # Query database user table to get a user with the specified username
        user = db.session.query(Users).filter(
            Users.username == username)

        if user:
            # A user with the specified username was found
            if user[0].username == username and user[0].password == password:
                # Set the user_id in the session for a successful login
                session['user_id'] = user[0].id
                return redirect('/notes')
        else:
            login_error_message = "Incorrect username or password"
    else:
        login_error_message = ""

    return render_template("login.html", error=login_error_message)


@main.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect("/")
