from flask import Blueprint, render_template, url_for, redirect, session, request
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks
from werkzeug.security import generate_password_hash, check_password_hash
import bleach
import datetime
current_date = datetime.datetime.now()

main = Blueprint('Index', __name__)


# def check_login(view_func):
#     def wrapped_view(*args, **kwargs):
#         if 'user_id' not in session:
#             # Redirect to the login page if not logged in
#             return redirect("/login")
#         return view_func(*args, **kwargs)
#     return wrapped_view


@main.route("/", methods=["GET"])
def index():

    return render_template("index/index.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("index/register.html")
    else:
        name_list = []
        check_username = db.session.query(Users).all()

        for names in check_username:
            name_list.append(names.username)

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        hashed_password = generate_password_hash(password)

        new_user = Users(username=username, password=hashed_password,
                         created_on=current_date, email=email)
        password_message = ""
        username_message = ""

        if password != confirm:
            password_message = "Password does not match!"

        if username in name_list:
            username_message = "Username not available!"

        if username_message or password_message:
            return render_template("index/register.html", message=password_message)
        else:
            db.session.add(new_user)
            db.session.commit()
            db.session.close()
        return redirect("/login")


@main.route("/login", methods=["GET", "POST"])
def login():

    session.clear()
    login_error_message = ""

    username = request.form.get("username")
    password = request.form.get("password")

    if request.method == "GET":

        return render_template("index/login.html")
    else:
        # Query database user table to get a user with the specified username
        user = db.session.query(Users).filter(
            Users.username == username).first()

        if user:
            # A user with the specified username was found
            if user.username == username and check_password_hash(user.password, password):
                # Set the user_id in the session for a successful login
                session['user_id'] = user.id
                return redirect('/notes')
        else:
            return render_template("index/login.html", error="Username / Password is not correct")
    return render_template("index/login.html", error="Username / Password is not correct")


@main.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect("/login")
