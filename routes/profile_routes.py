from flask import Blueprint, render_template, url_for, redirect, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks
import bleach
import datetime
current_date = datetime.datetime.now()

profiles = Blueprint('Profiles', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


@profiles.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        user = session['user_id']
        get_profile = db.session.query(Users).filter(Users.id == user).first()
    return render_template("index/profile.html", profile=get_profile)


@profiles.route("/edit_username", methods=["GET", "POST"])
def edit_username():
    user = session['user_id']
    get_login = db.session.query(Users).filter(Users.id == user).first()
    return render_template("profile/edit_username.html")


@profiles.route("/edit_password", methods=["GET", "POST"])
def edit_password():

    user = session['user_id']

    if request.method == "GET":

        return render_template("profile/change_password.html")

    else:

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")

        new_password_hashed = generate_password_hash(new_password)

        get_user_password = db.session.query(
            Users).filter(Users.id == user).first()

        if check_password_hash(get_user_password.password, current_password):
            get_user_password.password = new_password_hashed
            db.session.commit()
            db.session.close()
        else:
            return render_template("pr/change_password.html")
        return redirect('/notes')


@profiles.route("/edit_email", methods=["GET", "POST"])
def edit_email():
    return "email section"


@profiles.route("/delete_account", methods=["GET", "DELETE"])
def delete_user():

    user = session['user_id']
    delete_user_account = db.session.query(
        Users).filter(Users.id == user).first()
    if request.method == "GET":
        name = delete_user_account.username
        return render_template("profile/delete.html", name=name, id=delete_user_account.id)
    else:
        if delete_user_account.id == user:
            db.session.delete(delete_user_account)
            db.session.commit()
            db.session.close()

    return redirect("index/login.html")
