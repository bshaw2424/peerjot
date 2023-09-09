import os
from flask import Flask, render_template, request, flash, session, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from models import db, Users
from flask_migrate import Migrate
import datetime

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DB_URL')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Session(app)

app.secret_key = os.getenv('APP_SECRET')


db.init_app(app)
migrate = Migrate

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", time=datetime.datetime.now())


@app.route("/new_note")
def new_route():
    return render_template("notes.html")


@app.route("/note/<string:title>")
def note_page(title):
    return render_template("note_page.html", title=title)


@app.route("/note/<string:title>/<string:note>/")
def note(title, note):
    return render_template("note.html", title="hello", note="new note")

# @app.route("/logout")
# def logout():


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
