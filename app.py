import os
from flask import Flask, render_template, request, flash, session, jsonify, url_for, redirect
from sqlalchemy import text, select, update
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

# route modules
from routes.index_routes import main
from routes.block_routes import blocks
from routes.bookmark_routes import bookmarks
from routes.note_routes import note
from routes.page_routes import pages
from routes.sidnote_routes import sidenotes
from routes.profile_routes import profiles

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
            return redirect("/login")
        return view_func(*args, **kwargs)
    return wrapped_view


# index routes blueprint
app.register_blueprint(main, url_prefix='/')

# notes route blueprint
app.register_blueprint(note, url_prefix='/notes')

# blocks route blueprint
app.register_blueprint(
    blocks, url_prefix='/note/<string:block_title>/page/<string:block_page>/block')

# pages route blueprint
app.register_blueprint(
    pages, url_prefix='/note/<string:page_title>/page/<string:page_name>')

# bookmarks route blueprint
app.register_blueprint(
    bookmarks, url_prefix='/note/<string:bookmark_title>/page/<string:bookmark_page>/bookmark')

# sidenotes route blueprint
app.register_blueprint(
    sidenotes, url_prefix='/note/<string:sidenote_title>/page/<string:sidenote_page>/sidenote')

# profiles route blueprint
app.register_blueprint(
    profiles, url_prefix='/profile')


if __name__ == '__main__':
    app.run(debug=True)
