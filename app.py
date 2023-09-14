import os
from flask import Flask, render_template, request, flash, session, jsonify, url_for, redirect
from sqlalchemy.sql import text
from flask_session import Session
from helper import error_message
from werkzeug.security import generate_password_hash, check_password_hash
from formModels import NoteBlock
from dotenv import load_dotenv
import bleach
from models import db, Users
from flask_migrate import Migrate
import datetime
import secrets
current_date = datetime.datetime.now()
load_dotenv()  # take environment variables from .env.

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DB_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

Session(app)


db.init_app(app)
migrate = Migrate

with app.app_context():
    db.create_all()


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

        flash("account created successfully")
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    return render_template("login.html")


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    return render_template("dashboard.html", time=datetime.datetime.now())


@app.route("/new_note")
def new_route():
    return render_template("notes.html")


@app.route("/note/<string:title>", methods=['GET', 'POST'])
def note_page(title):
    return title


@app.route("/note/<string:title>/<string:note>/")
def note(title, note):
    return render_template("note.html", title="hello", note="new note")

# @app.route("/logout")
# def logout():


if __name__ == '__main__':
    app.run(debug=True)
