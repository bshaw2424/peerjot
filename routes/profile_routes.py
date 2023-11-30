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
    return render_template("index/profile.html", profile="Edit Profile", links=['one', 'two'])


@profiles.route("/profile_index", methods=["GET", "POST"])
def profile_index():
    if request.method == "GET":
        user = session['user_id']
    return render_template("profile/profile_index.html")


@profiles.route("/edit_username", methods=["GET", "POST"])
def edit_username():
    user = session['user_id']
    get_username = db.session.query(Users).filter(Users.id == user).first()

    if request.method == "GET":
        return render_template("profile/edit_username.html", get_username=get_username)
    else:
        if get_username:
            get_username.username = request.form.get("edit_username")
            db.session.commit()
            db.session.close()
            return redirect("/profile/account")
        else:
            return render_template("profile/edit_username.html", get_username=get_username)


@profiles.route("/edit_password", methods=["GET", "POST"])
def edit_password():

    user = session['user_id']

    if request.method == "GET":

        return render_template("profile/change_password.html")

    else:

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_changed_password")

        new_password_hashed = generate_password_hash(new_password)

        get_user_password = db.session.query(
            Users).filter(Users.id == user).first()

        if check_password_hash(get_user_password.password, current_password) and new_password == confirm_password:
            get_user_password.password = new_password_hashed
            db.session.commit()
            db.session.close()
        else:
            return render_template("profile/change_password.html", result="password does not match")
        return redirect('/profile/account')


@profiles.route("/account", methods=["GET", "POST"])
def account_settings():

    if request.method == "GET":
        return render_template("profile/account.html", account="Update Profile")


@profiles.route("/edit_email", methods=["GET", "POST"])
def edit_email():
    user = session['user_id']
    get_email = db.session.query(Users).filter(Users.id == user).first()

    if request.method == "GET":
        return render_template("profile/edit_email.html", value=get_email)
    else:
        if get_email:
            new_email = request.form.get("edit_email")
            get_email.email = new_email
            db.session.commit()
            return redirect("/profile/account")


@profiles.route("/delete_account", methods=["GET", "POST", "DELETE"])
def delete_user():

    user = session['user_id']
    delete_user_account = db.session.query(
        Users).filter(Users.id == user).first()
    if request.method == "GET":
        return render_template("profile/delete.html", delete_heading="Delete Account")
    else:
        if delete_user_account:
            db.session.delete(delete_user_account)
            db.session.commit()
            db.session.close()
            return redirect("/login")
        else:
            return render_template("profile/delete.html", delete_heading="Delete Account")
    return redirect("/login")
